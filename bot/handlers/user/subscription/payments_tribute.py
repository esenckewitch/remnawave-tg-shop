import logging
from typing import Optional

from aiogram import F, Router, types

from bot.keyboards.inline.user_keyboards import get_payment_url_keyboard
from bot.middlewares.i18n import JsonI18n
from bot.services.tribute_service import TributeService
from config.settings import Settings

router = Router(name="user_subscription_payments_tribute_router")


@router.callback_query(F.data.startswith("pay_tribute:"))
async def pay_tribute_callback_handler(
    callback: types.CallbackQuery,
    settings: Settings,
    i18n_data: dict,
    tribute_service: TributeService,
):
    """
    Handle Tribute payment callback.

    Tribute uses pre-configured payment links, so we just redirect the user
    to the appropriate Tribute payment page.
    """
    current_lang = i18n_data.get("current_language", settings.DEFAULT_LANGUAGE)
    i18n: Optional[JsonI18n] = i18n_data.get("i18n_instance")
    get_text = lambda key, **kwargs: i18n.gettext(current_lang, key, **kwargs) if i18n else key

    if not i18n or not callback.message:
        try:
            await callback.answer(get_text("error_occurred_try_again"), show_alert=True)
        except Exception:
            pass
        return

    if not settings.TRIBUTE_ENABLED:
        logging.error("Tribute payments are not enabled.")
        try:
            await callback.answer(get_text("payment_service_unavailable_alert"), show_alert=True)
        except Exception:
            pass
        return

    # Parse callback data: pay_tribute:{months}:{price}:{sale_mode}
    try:
        _, data_payload = callback.data.split(":", 1)
        parts = data_payload.split(":")
        months = int(float(parts[0]))
        price = float(parts[1])
        sale_mode = parts[2] if len(parts) > 2 else "subscription"
    except (ValueError, IndexError) as e:
        logging.error(f"Invalid pay_tribute data in callback: {callback.data}, error: {e}")
        try:
            await callback.answer(get_text("error_try_again"), show_alert=True)
        except Exception:
            pass
        return

    # Get the Tribute payment link for this duration
    payment_link = tribute_service.get_payment_link(months)

    if not payment_link:
        logging.error(f"Tribute: no payment link configured for {months} month(s)")
        try:
            await callback.answer(get_text("payment_service_unavailable_alert"), show_alert=True)
        except Exception:
            pass
        try:
            await callback.message.edit_text(get_text("payment_service_unavailable"))
        except Exception:
            pass
        return

    # Format the display value
    human_value = str(int(months)) if float(months).is_integer() else f"{months:g}"

    # Show payment link to user
    try:
        await callback.message.edit_text(
            get_text(
                key="payment_link_message_traffic" if sale_mode == "traffic" else "payment_link_message",
                months=months,
                traffic_gb=human_value,
            ),
            reply_markup=get_payment_url_keyboard(
                payment_link,
                current_lang,
                i18n,
                back_callback=f"subscribe_period:{human_value}",
                back_text_key="back_to_payment_methods_button",
            ),
            disable_web_page_preview=False,
        )
    except Exception as e:
        logging.warning(f"Tribute: failed to display payment link ({e}), sending new message.")
        try:
            await callback.message.answer(
                get_text(
                    key="payment_link_message_traffic" if sale_mode == "traffic" else "payment_link_message",
                    months=months,
                    traffic_gb=human_value,
                ),
                reply_markup=get_payment_url_keyboard(
                    payment_link,
                    current_lang,
                    i18n,
                    back_callback=f"subscribe_period:{human_value}",
                    back_text_key="back_to_payment_methods_button",
                ),
                disable_web_page_preview=False,
            )
        except Exception:
            pass

    try:
        await callback.answer()
    except Exception:
        pass
