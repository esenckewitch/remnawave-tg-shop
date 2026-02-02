import hashlib
import hmac
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from aiohttp import web
from aiogram import Bot
from sqlalchemy.orm import sessionmaker

from config.settings import Settings
from bot.middlewares.i18n import JsonI18n
from bot.services.subscription_service import SubscriptionService
from bot.services.referral_service import ReferralService
from bot.keyboards.inline.user_keyboards import get_connect_and_main_keyboard
from bot.services.notification_service import NotificationService
from db.dal import payment_dal, user_dal
from bot.utils.text_sanitizer import sanitize_display_name, username_for_display
from bot.utils.config_link import prepare_config_links


class TributeService:
    """
    Service for handling Tribute.tg payments.

    Tribute uses pre-configured product links. Users pay through Tribute,
    and we receive webhook notifications about successful payments.

    Webhook payload format:
    {
        "name": "new_digital_product",
        "created_at": "2025-03-20T01:15:58.332Z",
        "sent_at": "2025-03-20T01:15:58.542Z",
        "payload": {
            "product_id": 456,
            "amount": 500,
            "currency": "usd",
            "user_id": 31326,
            "telegram_user_id": 12321321
        }
    }

    Signature verification: HMAC-SHA256 of request body, signed with API key.
    Header: trbt-signature
    """

    def __init__(
        self,
        *,
        bot: Bot,
        settings: Settings,
        i18n: JsonI18n,
        async_session_factory: sessionmaker,
        subscription_service: SubscriptionService,
        referral_service: ReferralService,
    ):
        self.bot = bot
        self.settings = settings
        self.i18n = i18n
        self.async_session_factory = async_session_factory
        self.subscription_service = subscription_service
        self.referral_service = referral_service

        self.api_key: Optional[str] = settings.TRIBUTE_API_KEY
        self.default_currency: str = (settings.DEFAULT_CURRENCY_SYMBOL or "USD").upper()

        self.configured: bool = bool(
            settings.TRIBUTE_ENABLED and
            self.api_key and
            settings.tribute_links
        )

        if not self.configured:
            if settings.TRIBUTE_ENABLED:
                if not self.api_key:
                    logging.warning("TributeService: TRIBUTE_API_KEY is not set. Webhook verification disabled.")
                if not settings.tribute_links:
                    logging.warning("TributeService: No TRIBUTE_LINK_* configured. Tribute payments disabled.")
            else:
                logging.warning("TributeService initialized but not enabled (TRIBUTE_ENABLED=False).")

    def get_payment_link(self, months: int) -> Optional[str]:
        """Get the Tribute payment link for the specified subscription duration."""
        return self.settings.tribute_links.get(months)

    def _verify_signature(self, body: bytes, signature: str) -> bool:
        """Verify the webhook signature using HMAC-SHA256."""
        if not self.api_key:
            logging.warning("TributeService: Cannot verify signature - API key not configured")
            return False

        if not signature:
            return False

        expected = hmac.new(
            self.api_key.encode("utf-8"),
            body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected.lower(), signature.lower())

    def _parse_months_from_product(self, product_id: int, amount: float) -> int:
        """
        Try to determine subscription months from the product.
        This maps Tribute product IDs to months based on configured links.
        Falls back to 1 month if unknown.
        """
        # Check if product_id matches any known link pattern
        for months, link in self.settings.tribute_links.items():
            # Extract product ID from link if possible
            # Links are like https://t.me/tribute/app?startapp=p{id} or https://web.tribute.tg/p/{id}
            if f"p{product_id}" in link or f"p/{product_id}" in link:
                return months

        # Fallback: try to infer from amount
        # This is a heuristic - you might want to customize this
        return 1

    async def webhook_route(self, request: web.Request) -> web.Response:
        """Handle incoming Tribute webhooks."""
        if not self.settings.TRIBUTE_ENABLED:
            return web.Response(status=503, text="tribute_disabled")

        # Read raw body for signature verification
        try:
            body = await request.read()
        except Exception as e:
            logging.error(f"Tribute webhook: failed to read body: {e}")
            return web.Response(status=400, text="bad_request")

        # Verify signature
        signature = request.headers.get("trbt-signature", "")
        if self.api_key and not self._verify_signature(body, signature):
            logging.error("Tribute webhook: invalid signature")
            return web.Response(status=403, text="invalid_signature")

        # Parse JSON payload
        try:
            data = json.loads(body)
        except json.JSONDecodeError as e:
            logging.error(f"Tribute webhook: invalid JSON: {e}")
            return web.Response(status=400, text="invalid_json")

        event_name = data.get("name", "")
        payload = data.get("payload", {})

        logging.info(f"Tribute webhook received: event={event_name}, payload={payload}")

        # Handle different event types
        if event_name == "new_digital_product":
            return await self._handle_new_digital_product(data, payload)
        elif event_name == "digitalProductRefund":
            logging.info(f"Tribute webhook: refund received for product {payload.get('product_id')}")
            return web.Response(text="OK")
        elif event_name in ("newSubscription", "renewedSubscription"):
            return await self._handle_subscription_event(data, payload)
        elif event_name == "cancelledSubscription":
            logging.info(f"Tribute webhook: subscription cancelled for user {payload.get('telegram_user_id')}")
            return web.Response(text="OK")
        else:
            logging.warning(f"Tribute webhook: unknown event type '{event_name}'")
            return web.Response(text="OK")

    async def _handle_new_digital_product(
        self,
        data: Dict[str, Any],
        payload: Dict[str, Any]
    ) -> web.Response:
        """Handle new digital product purchase."""
        telegram_user_id = payload.get("telegram_user_id")
        product_id = payload.get("product_id")
        amount = payload.get("amount", 0)
        currency = payload.get("currency", "usd").upper()
        tribute_user_id = payload.get("user_id")  # Tribute's internal user ID

        if not telegram_user_id:
            logging.error("Tribute webhook: missing telegram_user_id in payload")
            return web.Response(status=400, text="missing_telegram_user_id")

        try:
            telegram_user_id = int(telegram_user_id)
        except (TypeError, ValueError):
            logging.error(f"Tribute webhook: invalid telegram_user_id: {telegram_user_id}")
            return web.Response(status=400, text="invalid_telegram_user_id")

        # Determine subscription duration from product
        months = self._parse_months_from_product(product_id, amount)

        # Convert amount to float (Tribute sends cents/smallest units for some currencies)
        amount_float = float(amount) / 100 if currency in ("USD", "EUR") else float(amount)

        async with self.async_session_factory() as session:
            # Check if user exists
            db_user = await user_dal.get_user_by_id(session, telegram_user_id)
            if not db_user:
                logging.warning(f"Tribute webhook: user {telegram_user_id} not found in database")
                # Create a minimal user record
                try:
                    db_user = await user_dal.create_user(session, {
                        "user_id": telegram_user_id,
                        "first_name": "Tribute User",
                        "language_code": self.settings.DEFAULT_LANGUAGE,
                    })
                    await session.commit()
                    logging.info(f"Tribute webhook: created new user {telegram_user_id}")
                except Exception as e:
                    logging.error(f"Tribute webhook: failed to create user {telegram_user_id}: {e}")
                    return web.Response(status=500, text="user_creation_failed")

            # Create payment record
            provider_payment_id = f"tribute:{product_id}:{tribute_user_id}:{data.get('created_at', '')}"

            # Check for duplicate
            existing = await payment_dal.get_payment_by_provider_payment_id(session, provider_payment_id)
            if existing:
                logging.info(f"Tribute webhook: duplicate payment {provider_payment_id}, already processed")
                return web.Response(text="OK")

            payment_record_payload = {
                "user_id": telegram_user_id,
                "amount": amount_float,
                "currency": currency,
                "status": "succeeded",
                "description": f"Tribute subscription {months} month(s)",
                "subscription_duration_months": months,
                "provider": "tribute",
                "provider_payment_id": provider_payment_id,
            }

            try:
                payment_record = await payment_dal.create_payment_record(session, payment_record_payload)
                await session.commit()
                logging.info(f"Tribute: payment record {payment_record.payment_id} created for user {telegram_user_id}")
            except Exception as e:
                await session.rollback()
                logging.error(f"Tribute webhook: failed to create payment record: {e}", exc_info=True)
                return web.Response(status=500, text="db_error")

            # Activate subscription
            activation = None
            referral_bonus = None
            sale_mode = "traffic" if self.settings.traffic_sale_mode else "subscription"

            try:
                activation = await self.subscription_service.activate_subscription(
                    session,
                    telegram_user_id,
                    int(months) if sale_mode != "traffic" else 0,
                    amount_float,
                    payment_record.payment_id,
                    provider="tribute",
                    sale_mode=sale_mode,
                    traffic_gb=months if sale_mode == "traffic" else None,
                )

                if sale_mode != "traffic":
                    referral_bonus = await self.referral_service.apply_referral_bonuses_for_payment(
                        session,
                        telegram_user_id,
                        int(months),
                        current_payment_db_id=payment_record.payment_id,
                        skip_if_active_before_payment=False,
                    )

                await session.commit()
            except Exception as e:
                await session.rollback()
                logging.error(f"Tribute webhook: failed to activate subscription: {e}", exc_info=True)
                return web.Response(status=500, text="activation_error")

            # Send notification to user
            await self._send_success_notification(
                session,
                telegram_user_id,
                months,
                activation,
                referral_bonus,
                sale_mode,
                db_user,
                amount_float,
                currency,
            )

        return web.Response(text="OK")

    async def _handle_subscription_event(
        self,
        data: Dict[str, Any],
        payload: Dict[str, Any]
    ) -> web.Response:
        """Handle subscription events (new or renewed)."""
        # Similar to digital product, but for recurring subscriptions
        telegram_user_id = payload.get("telegram_user_id")
        if not telegram_user_id:
            logging.error("Tribute subscription webhook: missing telegram_user_id")
            return web.Response(status=400, text="missing_telegram_user_id")

        # For subscriptions, we might receive different payload structure
        # Process similarly to digital products
        return await self._handle_new_digital_product(data, payload)

    async def _send_success_notification(
        self,
        session,
        user_id: int,
        months: int,
        activation: Optional[Dict[str, Any]],
        referral_bonus: Optional[Dict[str, Any]],
        sale_mode: str,
        db_user,
        amount: float,
        currency: str,
    ):
        """Send payment success notification to user."""
        lang = db_user.language_code if db_user and db_user.language_code else self.settings.DEFAULT_LANGUAGE
        _ = lambda k, **kw: self.i18n.gettext(lang, k, **kw) if self.i18n else k

        raw_config_link = activation.get("subscription_url") if activation else None
        config_link_display, connect_button_url = await prepare_config_links(self.settings, raw_config_link)
        config_link_text = config_link_display or _("config_link_not_available")

        final_end = activation.get("end_date") if activation else None
        applied_days = 0

        if referral_bonus and referral_bonus.get("referee_new_end_date"):
            final_end = referral_bonus["referee_new_end_date"]
            applied_days = referral_bonus.get("referee_bonus_applied_days", 0)

        if not final_end and activation and activation.get("end_date"):
            final_end = activation["end_date"]

        end_date_str = final_end.strftime("%Y-%m-%d") if final_end else _("config_link_not_available")
        traffic_label = str(int(months)) if float(months).is_integer() else f"{months:g}"

        if sale_mode == "traffic":
            text = _("payment_successful_traffic_full",
                     traffic_gb=traffic_label,
                     end_date=end_date_str if final_end else "",
                     config_link=config_link_text)
        elif applied_days:
            inviter_name_display = _("friend_placeholder")
            if db_user and db_user.referred_by_id:
                inviter = await user_dal.get_user_by_id(session, db_user.referred_by_id)
                if inviter:
                    safe_name = sanitize_display_name(inviter.first_name) if inviter.first_name else None
                    if safe_name:
                        inviter_name_display = safe_name
                    elif inviter.username:
                        inviter_name_display = username_for_display(inviter.username, with_at=False)
            text = _(
                "payment_successful_with_referral_bonus_full",
                months=months,
                base_end_date=activation["end_date"].strftime("%Y-%m-%d") if activation and activation.get("end_date") else end_date_str,
                bonus_days=applied_days,
                final_end_date=end_date_str,
                inviter_name=inviter_name_display,
                config_link=config_link_text,
            )
        else:
            text = _(
                "payment_successful_full",
                months=months,
                end_date=end_date_str,
                config_link=config_link_text,
            )

        markup = get_connect_and_main_keyboard(
            lang,
            self.i18n,
            self.settings,
            config_link_display,
            connect_button_url=connect_button_url,
            preserve_message=True,
        )

        try:
            await self.bot.send_message(
                user_id,
                text,
                reply_markup=markup,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        except Exception as e:
            logging.error(f"Tribute notification: failed to send message to user {user_id}: {e}")

        # Notify admins
        try:
            notification_service = NotificationService(self.bot, self.settings, self.i18n)
            await notification_service.notify_payment_received(
                user_id=user_id,
                amount=amount,
                currency=currency,
                months=int(months) if sale_mode != "traffic" else 0,
                traffic_gb=months if sale_mode == "traffic" else None,
                payment_provider="tribute",
                username=db_user.username if db_user else None,
            )
        except Exception as e:
            logging.error(f"Tribute notification: failed to notify admins: {e}")

    async def close(self) -> None:
        """Cleanup resources."""
        pass


async def tribute_webhook_route(request: web.Request) -> web.Response:
    """Webhook route handler for Tribute."""
    service: TributeService = request.app["tribute_service"]
    return await service.webhook_route(request)
