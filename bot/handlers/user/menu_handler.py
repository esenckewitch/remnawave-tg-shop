"""Handler for /menu command and reply keyboard buttons."""
import logging
from aiogram import Router, F, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from bot.services.subscription_service import SubscriptionService
from config.settings import Settings
from bot.middlewares.i18n import JsonI18n

router = Router(name="menu_handler_router")


@router.message(Command("menu"))
async def menu_command_handler(
    message: types.Message,
    settings: Settings,
    i18n_data: dict,
    subscription_service: SubscriptionService,
    session: AsyncSession,
):
    """Handle /menu command - show inline keyboard menu."""
    from .start import send_main_menu

    # Просто показываем главное меню с inline кнопками
    await send_main_menu(
        message,
        settings,
        i18n_data,
        subscription_service,
        session,
        is_edit=False
    )


@router.message(F.text & ~F.text.startswith("/"))
async def reply_button_handler(
    message: types.Message,
    state: FSMContext,
    settings: Settings,
    i18n_data: dict,
    subscription_service: SubscriptionService,
    panel_service,
    referral_service,
    session: AsyncSession,
    bot: Bot,
):
    """Handle text messages from reply keyboard buttons."""
    current_lang = i18n_data.get("current_language", settings.DEFAULT_LANGUAGE)
    i18n: JsonI18n = i18n_data.get("i18n_instance")

    if not i18n or not message.text:
        return

    _ = lambda key, **kwargs: i18n.gettext(current_lang, key, **kwargs)

    # Map button text to callback actions
    button_text = message.text.strip()

    # Import handlers
    from . import subscription as user_subscription_handlers
    from . import referral as user_referral_handlers
    from . import trial_handler as user_trial_handlers
    from . import start as user_start_handlers

    # Check which button was pressed by comparing with translations
    if button_text == _(key="menu_subscribe_inline"):
        # Subscribe button
        await user_subscription_handlers.display_subscription_options(
            message, i18n_data, settings, session
        )

    elif button_text == _(key="menu_my_subscription_inline"):
        # My subscription button
        await user_subscription_handlers.my_subscription_command_handler(
            message, i18n_data, settings,
            panel_service,
            subscription_service,
            session,
            bot,
        )

    elif button_text == _(key="menu_referral_inline"):
        # Referrals button
        await user_referral_handlers.referral_command_handler(
            message, settings, i18n_data,
            referral_service,
            bot,
            session,
        )

    elif button_text == _(key="menu_activate_trial_button"):
        # Trial button
        await user_trial_handlers.request_trial_confirmation_handler(
            message, settings, i18n_data, subscription_service, session
        )

    elif button_text == _(key="menu_support_button"):
        # Support button - just show support link
        if settings.SUPPORT_LINK:
            await message.answer(
                f"💬 {_(key='menu_support_button')}: {settings.SUPPORT_LINK}"
            )

    elif button_text == _(key="menu_language_settings_inline"):
        # Language button
        await user_start_handlers.language_command_handler(
            message, i18n_data, settings
        )
