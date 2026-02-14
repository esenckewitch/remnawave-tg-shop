"""
Payment Status Tracker
Отслеживает статус оплаты и отправляет промежуточные сообщения пользователю
"""

import asyncio
import logging
from typing import Optional
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from bot.middlewares.i18n import JsonI18n


async def track_payment_status(
    bot: Bot,
    user_id: int,
    payment_id: str,
    i18n: Optional[JsonI18n],
    current_lang: str,
    session: AsyncSession,
    provider: str = "yookassa",
):
    """
    Отслеживание статуса оплаты и отправка промежуточных сообщений.

    Args:
        bot: Telegram bot instance
        user_id: ID пользователя
        payment_id: ID платежа в нашей БД или provider payment ID
        i18n: Инстанс локализации
        current_lang: Текущий язык пользователя
        session: DB session
        provider: Платёжная система (yookassa, freekassa, etc.)
    """
    _ = lambda key, **kwargs: i18n.gettext(current_lang, key, **kwargs) if i18n else key

    try:
        # Шаг 1: Сразу после создания платежа
        logging.info(f"Payment tracker started for user {user_id}, payment {payment_id}")

        await bot.send_message(
            user_id,
            _("payment_redirect_message"),
            parse_mode="HTML"
        )

        # Шаг 2: Ждём 30 секунд
        await asyncio.sleep(30)

        # Проверяем статус платежа
        from db.dal import payment_dal

        payment = None
        try:
            # Пробуем найти по provider_payment_id
            payment = await payment_dal.get_payment_by_provider_id(session, payment_id)

            # Если не нашли, пробуем по внутреннему ID
            if not payment:
                try:
                    internal_id = int(payment_id)
                    payment = await payment_dal.get_payment_by_id(session, internal_id)
                except ValueError:
                    pass
        except Exception as e:
            logging.error(f"Error fetching payment {payment_id}: {e}")

        if not payment or payment.status in ["pending", "created"]:
            # Платёж ещё в ожидании
            logging.info(f"Payment {payment_id} still pending after 30s")

            await bot.send_message(
                user_id,
                _("payment_checking_message"),
                parse_mode="HTML"
            )

            # Шаг 3: Ждём ещё 4.5 минуты
            await asyncio.sleep(270)

            # Повторная проверка
            try:
                if payment:
                    await session.refresh(payment)
            except Exception as e:
                logging.error(f"Error refreshing payment {payment_id}: {e}")
                payment = await payment_dal.get_payment_by_provider_id(session, payment_id)

            if not payment or payment.status in ["pending", "created"]:
                # Всё ещё в ожидании — отправляем финальное сообщение
                logging.warning(f"Payment {payment_id} still pending after 5 minutes")

                await bot.send_message(
                    user_id,
                    _("payment_delayed_message"),
                    parse_mode="HTML"
                )
        else:
            # Платёж уже обработан (успешно или неуспешно)
            logging.info(f"Payment {payment_id} already processed with status: {payment.status}")

    except asyncio.CancelledError:
        logging.info(f"Payment tracker cancelled for user {user_id}, payment {payment_id}")
        raise

    except Exception as e:
        logging.error(f"Error in payment tracker for user {user_id}: {e}", exc_info=True)


def start_payment_tracking(
    bot: Bot,
    user_id: int,
    payment_id: str,
    i18n: Optional[JsonI18n],
    current_lang: str,
    session: AsyncSession,
    provider: str = "yookassa",
):
    """
    Запускает трекинг оплаты в фоновом режиме.

    Использовать так:
        start_payment_tracking(
            bot=callback.bot,
            user_id=user_id,
            payment_id=created_payment.provider_payment_id,
            i18n=i18n,
            current_lang=current_lang,
            session=session,
            provider="yookassa",
        )
    """
    task = asyncio.create_task(
        track_payment_status(
            bot=bot,
            user_id=user_id,
            payment_id=payment_id,
            i18n=i18n,
            current_lang=current_lang,
            session=session,
            provider=provider,
        )
    )

    # Обработка ошибок в фоновой задаче
    def handle_task_result(t: asyncio.Task):
        try:
            t.result()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logging.error(f"Payment tracker task failed: {e}", exc_info=True)

    task.add_done_callback(handle_task_result)

    return task
