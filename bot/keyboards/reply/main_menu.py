"""Main menu reply keyboard with colored buttons (Bot API 9.4+)."""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from typing import List
from config.settings import Settings


def get_main_menu_reply_keyboard(
    lang: str,
    i18n_instance,
    settings: Settings,
    show_trial_button: bool = False,
) -> ReplyKeyboardMarkup:
    """
    Create main menu reply keyboard with colored buttons.

    Button styles (Bot API 9.4):
    - primary: Blue button (main action)
    - secondary: Gray button (default)
    - success: Green button (positive action)
    - danger: Red button (destructive action)
    """
    _ = lambda key, **kwargs: i18n_instance.gettext(lang, key, **kwargs)

    keyboard_rows: List[List[KeyboardButton]] = []

    # Row 1: Trial button (if enabled)
    if show_trial_button and settings.TRIAL_ENABLED:
        keyboard_rows.append([
            KeyboardButton(
                text=_(key="menu_activate_trial_button"),
            )
        ])

    # Row 2: Subscribe button (main action)
    keyboard_rows.append([
        KeyboardButton(
            text=_(key="menu_subscribe_inline"),
        )
    ])

    # Row 3: My subscription + Referrals
    row_3 = []
    row_3.append(
        KeyboardButton(
            text=_(key="menu_my_subscription_inline"),
        )
    )
    row_3.append(
        KeyboardButton(
            text=_(key="menu_referral_inline"),
        )
    )
    keyboard_rows.append(row_3)

    # Row 4: Support + Language (if support enabled)
    row_4 = []
    if settings.SUPPORT_LINK:
        row_4.append(
            KeyboardButton(
                text=_(key="menu_support_button"),
            )
        )
    row_4.append(
        KeyboardButton(
            text=_(key="menu_language_settings_inline"),
        )
    )
    if row_4:
        keyboard_rows.append(row_4)

    return ReplyKeyboardMarkup(
        keyboard=keyboard_rows,
        resize_keyboard=True,
        input_field_placeholder=_(key="menu_input_placeholder") if i18n_instance else "Выберите действие...",
    )


def get_hide_menu_keyboard() -> ReplyKeyboardMarkup:
    """Create a keyboard that hides the reply keyboard."""
    from aiogram.types import ReplyKeyboardRemove
    return ReplyKeyboardRemove()
