import asyncio
import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from sqlalchemy.orm import sessionmaker

from bot.keyboards.inline.user_keyboards import get_subscribe_only_markup
from bot.middlewares.i18n import JsonI18n
from config.settings import Settings
from db.dal import winback_dal


class WinbackService:
    def __init__(
        self,
        bot: Bot,
        settings: Settings,
        i18n: JsonI18n,
        async_session_factory: sessionmaker,
    ):
        self.bot = bot
        self.settings = settings
        self.i18n = i18n
        self.async_session_factory = async_session_factory

    async def run_periodic_check(self):
        interval = self.settings.WINBACK_CHECK_INTERVAL_HOURS * 3600
        logging.info(
            "WinbackService: periodic check started (every %d hours)",
            self.settings.WINBACK_CHECK_INTERVAL_HOURS,
        )
        while True:
            try:
                await self._check_and_notify()
            except asyncio.CancelledError:
                raise
            except Exception:
                logging.exception("WinbackService: error during periodic check")
            await asyncio.sleep(interval)

    async def _check_and_notify(self):
        async with self.async_session_factory() as session:
            subscriptions = await winback_dal.get_users_for_winback(session, days_after_expiry=3)

            if not subscriptions:
                logging.debug("WinbackService: no winback-eligible users found")
                return

            logging.info("WinbackService: found %d winback-eligible users", len(subscriptions))

            for sub in subscriptions:
                user = sub.user
                if not user:
                    continue

                user_id = user.user_id
                lang = user.language_code or self.settings.DEFAULT_LANGUAGE
                first_name = user.first_name or f"User {user_id}"

                try:
                    discount = await winback_dal.create_winback_discount(
                        session,
                        user_id=user_id,
                        discount_percent=self.settings.WINBACK_DISCOUNT_PERCENT,
                        validity_days=self.settings.WINBACK_DISCOUNT_VALIDITY_DAYS,
                    )
                    await session.flush()

                    _ = lambda key, **kwargs: self.i18n.gettext(lang, key, **kwargs)

                    markup = get_subscribe_only_markup(lang, self.i18n)

                    try:
                        await self.bot.send_message(
                            user_id,
                            _(
                                "winback_discount_notification",
                                user_name=first_name,
                                discount_percent=self.settings.WINBACK_DISCOUNT_PERCENT,
                                validity_days=self.settings.WINBACK_DISCOUNT_VALIDITY_DAYS,
                            ),
                            reply_markup=markup,
                        )
                        logging.info(
                            "WinbackService: sent discount notification to user %d", user_id
                        )
                    except Exception:
                        logging.warning(
                            "WinbackService: failed to send message to user %d", user_id
                        )

                except Exception:
                    logging.exception(
                        "WinbackService: failed to create discount for user %d", user_id
                    )

            await session.commit()
