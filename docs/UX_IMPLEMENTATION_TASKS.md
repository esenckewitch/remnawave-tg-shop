# 📋 ДЕТАЛЬНЫЙ ПЛАН ЗАДАЧ — UX УЛУЧШЕНИЯ

**Дата:** 2026-02-14
**Базовый документ:** `docs/UX_AUDIT_2026-02-14.md`
**Общее время:** 10-12 дней
**Цель:** Увеличить конверсию на 400-700%

---

## 🎯 ФАЗА 1: QUICK WINS (1-2 дня)

### ✅ ЗАДАЧА 1.1: Добавить feedback на все кнопки

**Приоритет:** 🔴 Критично
**Время:** 2 часа
**Цель:** Устранить 48 случаев повторных кликов

#### Подзадачи:

**1.1.1. Обновить `bot/handlers/user/start.py`**

Найти функцию `main_action_callback_handler` (строка ~671) и добавить feedback:

```python
@router.callback_query(F.data.startswith("main_action:"))
async def main_action_callback_handler(
        callback: types.CallbackQuery, state: FSMContext, settings: Settings,
        i18n_data: dict, bot: Bot, subscription_service: SubscriptionService,
        referral_service: ReferralService, panel_service: PanelApiService,
        promo_code_service: PromoCodeService, session: AsyncSession):

    # ✅ ДОБАВИТЬ ЭТУ СТРОКУ В САМОМ НАЧАЛЕ
    await callback.answer()

    action = callback.data.split(":")[1]
    user_id = callback.from_user.id
    # ... остальной код
```

**1.1.2. Обновить `bot/handlers/user/subscription/core.py`**

Найти функцию `reshow_subscription_options_callback` (строка ~106):

```python
@router.callback_query(F.data == "main_action:subscribe")
async def reshow_subscription_options_callback(callback: types.CallbackQuery, i18n_data: dict, settings: Settings, session: AsyncSession):
    # ✅ ДОБАВИТЬ
    await callback.answer()

    await display_subscription_options(callback, i18n_data, settings, session)
```

**1.1.3. Обновить все callback handlers в subscription/**

Файлы для проверки:
- `bot/handlers/user/subscription/payments.py`
- `bot/handlers/user/subscription/payments_yookassa.py`
- `bot/handlers/user/subscription/payments_freekassa.py`
- `bot/handlers/user/subscription/payments_platega.py`
- `bot/handlers/user/subscription/payments_crypto.py`
- `bot/handlers/user/subscription/payments_stars.py`
- `bot/handlers/user/subscription/payments_tribute.py`

В каждом callback handler добавить в начало:
```python
await callback.answer()
```

**Чеклист:**
- [ ] Добавлен feedback в `main_action_callback_handler`
- [ ] Добавлен feedback в `reshow_subscription_options_callback`
- [ ] Проверены все payment handlers
- [ ] Проверены все callback_query декораторы
- [ ] Протестировано на локальном боте (нет повторных кликов)

---

### ✅ ЗАДАЧА 1.2: Обновить тексты локализации

**Приоритет:** 🔴 Критично
**Время:** 1 час
**Цель:** Упростить язык, убрать жаргон

#### Подзадачи:

**1.2.1. Обновить приветственное сообщение**

**Файл:** `locales/ru.json`

Найти строку 2 и заменить:

```json
{
  "welcome": "Привет, {user_name}! 👋\n\nYouTube, Instagram снова работают 🚀\nБыстро. Просто. Бесплатно на 3 дня.\n\nЖми «Попробовать» — займёт 1 минуту 👇"
}
```

**1.2.2. Переименовать кнопки главного меню**

**Файл:** `locales/ru.json`

Найти строки 11-13 и заменить:

```json
{
  "menu_activate_trial_button": "🎁 7 дней бесплатно — попробовать",
  "menu_subscribe_inline": "⚡ Выбрать тариф",
  "main_menu_greeting": "Начни с бесплатного пробного периода 👇"
}
```

**1.2.3. Упростить сообщение после активации триала**

**Файл:** `locales/ru.json`

Найти строку 88 и заменить:

```json
{
  "trial_activated_details_message": "🎉 Ура! 3 дня VPN — твои!\n\nОсталось 1 шаг — установить приложение (займёт 1 минуту)\n\nЖми «Подключиться» 👇"
}
```

**1.2.4. Улучшить сообщения об ошибках**

**Файл:** `locales/ru.json`

Найти строки 25-26 и заменить:

```json
{
  "error_occurred_try_again": "Что-то пошло не так 😔\n\nПопробуй ещё раз или напиши в поддержку — поможем!\n👉 @Forours_Helper",
  "error_try_again": "Не получилось... Попробуй снова через минуту или напиши нам 👉 @Forours_Helper"
}
```

**1.2.5. Улучшить уведомление об успешной оплате**

**Файл:** `locales/ru.json`

Найти строку 72 и заменить:

```json
{
  "payment_successful_full": "🎉 Спасибо! Подписка оформлена ❤️\n\n✅ Активна до {end_date}\n\nТеперь подключимся, если еще не подключились — это займёт минуту 👇"
}
```

**1.2.6. Улучшить alert при активации триала**

**Файл:** `locales/ru.json`

Найти строку 87 и заменить:

```json
{
  "trial_activated_alert": "Ура! 🎉 Твой бесплатный VPN активирован!"
}
```

**Чеклист:**
- [ ] Обновлен `welcome`
- [ ] Обновлены кнопки меню
- [ ] Обновлено `trial_activated_details_message`
- [ ] Обновлены сообщения об ошибках
- [ ] Обновлено `payment_successful_full`
- [ ] Обновлен `trial_activated_alert`
- [ ] Проверена корректность JSON (нет ошибок парсинга)
- [ ] Протестированы все обновлённые тексты в боте

---

### ✅ ЗАДАЧА 1.3: Убрать reply keyboard

**Приоритет:** 🔴 Критично
**Время:** 30 минут
**Цель:** Упростить интерфейс, убрать дублирование

#### Подзадачи:

**1.3.1. Удалить reply keyboard из start handler**

**Файл:** `bot/handlers/user/start.py`

Найти строки ~463-476 и изменить:

```python
# БЫЛО:
if not settings.DISABLE_WELCOME_MESSAGE:
    show_trial_for_keyboard = False
    if settings.TRIAL_ENABLED:
        if not await subscription_service.has_had_any_subscription(session, user_id):
            show_trial_for_keyboard = True

    reply_keyboard = get_main_menu_reply_keyboard(
        current_lang, i18n, settings, show_trial_for_keyboard
    )
    await message.answer(
        _(key="welcome", user_name=hd.quote(user.full_name)),
        reply_markup=reply_keyboard  # ❌ УДАЛИТЬ ЭТУ СТРОКУ
    )

# СТАЛО:
if not settings.DISABLE_WELCOME_MESSAGE:
    await message.answer(
        _(key="welcome", user_name=hd.quote(user.full_name))
        # ✅ Без reply_markup
    )
```

**1.3.2. Удалить reply keyboard из verify_channel_subscription_callback**

**Файл:** `bot/handlers/user/start.py`

Найти строки ~564-573 и изменить:

```python
# БЫЛО:
if not settings.DISABLE_WELCOME_MESSAGE:
    welcome_text = _(key="welcome",
                     user_name=hd.quote(callback.from_user.full_name))
    if callback.message:
        await callback.message.answer(welcome_text)

# СТАЛО (оставить как есть, reply_markup уже не передаётся):
if not settings.DISABLE_WELCOME_MESSAGE:
    welcome_text = _(key="welcome",
                     user_name=hd.quote(callback.from_user.full_name))
    if callback.message:
        await callback.message.answer(welcome_text)
```

**1.3.3. (Опционально) Удалить неиспользуемые файлы**

Если больше нигде не используется:
- `bot/keyboards/reply/main_menu.py` — можно оставить для будущего использования

**Чеклист:**
- [ ] Удалён `reply_markup` из приветственного сообщения
- [ ] Проверено что нет других мест с reply keyboard
- [ ] Протестировано — бот работает без reply keyboard
- [ ] UI выглядит чище

---

### ✅ ЗАДАЧА 1.4: Добавить промежуточные статусы оплаты

**Приоритет:** 🔴 Критично
**Время:** 4 часа
**Цель:** Снизить payment drop-off с 90.7% до 40-50%

#### Подзадачи:

**1.4.1. Создать модуль трекинга оплаты**

**Новый файл:** `bot/handlers/user/subscription/payment_status_tracker.py`

Создать файл со следующим содержимым:

```python
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
```

**1.4.2. Добавить новые ключи локализации**

**Файл:** `locales/ru.json`

Добавить после существующих ключей (например, после строки 495):

```json
{
  "payment_redirect_message": "Переходим к оплате... 💳\n\nКак оплатишь — сразу получишь доступ! 🚀",
  "payment_checking_message": "⏳ Проверяем оплату...\n\nОбычно это занимает 10-30 секунд",
  "payment_delayed_message": "Оплата всё ещё проверяется... ⏰\n\nЕсли что-то пошло не так — напиши нам:\n@Forours_Helper\n\nМы поможем!"
}
```

**Также добавить в `locales/en.json`:**

```json
{
  "payment_redirect_message": "Redirecting to payment... 💳\n\nOnce you pay — you'll get instant access! 🚀",
  "payment_checking_message": "⏳ Checking payment...\n\nUsually takes 10-30 seconds",
  "payment_delayed_message": "Payment is still being verified... ⏰\n\nIf something went wrong — contact support:\n@Forours_Helper\n\nWe'll help!"
}
```

**1.4.3. Интегрировать трекер в YooKassa handler**

**Файл:** `bot/handlers/user/subscription/payments_yookassa.py`

Найти место где создаётся платёж и отправляется ссылка пользователю, добавить:

```python
# В начале файла добавить импорт:
from .payment_status_tracker import start_payment_tracking

# Найти функцию создания платежа (примерно строка ~50-150)
# После создания payment_url и отправки пользователю добавить:

# Пример:
async def handle_yookassa_payment(...):
    # ... существующий код создания платежа

    # После создания платежа:
    payment_url = created_payment.confirmation.confirmation_url

    # Отправляем ссылку пользователю
    await callback.message.answer(
        _("payment_link_message", months=months),
        reply_markup=get_payment_url_keyboard(payment_url, current_lang, i18n)
    )

    # ✅ ДОБАВИТЬ ТРЕКИНГ
    start_payment_tracking(
        bot=callback.bot,
        user_id=user_id,
        payment_id=created_payment.id,  # или provider_payment_id
        i18n=i18n,
        current_lang=current_lang,
        session=session,
        provider="yookassa",
    )
```

**1.4.4. Интегрировать трекер в другие payment handlers**

Повторить процесс для:
- `bot/handlers/user/subscription/payments_freekassa.py`
- `bot/handlers/user/subscription/payments_platega.py`
- `bot/handlers/user/subscription/payments_crypto.py`
- `bot/handlers/user/subscription/payments_stars.py`
- `bot/handlers/user/subscription/payments_tribute.py`

В каждом после создания платежа добавить:

```python
from .payment_status_tracker import start_payment_tracking

# После отправки payment_url:
start_payment_tracking(
    bot=callback.bot,
    user_id=user_id,
    payment_id=payment.provider_payment_id,
    i18n=i18n,
    current_lang=current_lang,
    session=session,
    provider="<название провайдера>",
)
```

**1.4.5. Добавить метод в payment_dal для поиска платежа**

**Файл:** `db/dal/payment_dal.py`

Проверить что есть методы:

```python
async def get_payment_by_provider_id(
    session: AsyncSession,
    provider_payment_id: str
) -> Optional[Payment]:
    """Получить платёж по provider_payment_id"""
    stmt = select(Payment).where(
        Payment.provider_payment_id == provider_payment_id
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_payment_by_id(
    session: AsyncSession,
    payment_id: int
) -> Optional[Payment]:
    """Получить платёж по внутреннему ID"""
    return await session.get(Payment, payment_id)
```

Если нет — добавить.

**Чеклист:**
- [ ] Создан файл `payment_status_tracker.py`
- [ ] Добавлены ключи локализации (ru + en)
- [ ] Интегрирован в `payments_yookassa.py`
- [ ] Интегрирован в `payments_freekassa.py`
- [ ] Интегрирован в `payments_platega.py`
- [ ] Интегрирован в `payments_crypto.py`
- [ ] Интегрирован в `payments_stars.py`
- [ ] Интегрирован в `payments_tribute.py`
- [ ] Проверены методы в `payment_dal.py`
- [ ] Протестировано на тестовом платеже
- [ ] Проверены логи — нет ошибок
- [ ] Пользователь получает все 3 сообщения

---

## 📊 КОНТРОЛЬНАЯ ТОЧКА ФАЗЫ 1

После завершения всех задач Фазы 1:

**Тестирование:**
1. Запустить бота локально
2. Пройти полный путь: /start → Trial → Подключение
3. Пройти путь: /start → Subscribe → Payment
4. Проверить что нет повторных кликов
5. Проверить что тексты изменены
6. Проверить что reply keyboard исчезла
7. Проверить что приходят сообщения о статусе оплаты

**Метрики для проверки:**
- [ ] Нет повторных кликов при нажатии кнопок
- [ ] Тексты читаются легко, без жаргона
- [ ] Интерфейс стал чище (нет дублирования клавиатур)
- [ ] При оплате приходят промежуточные сообщения

**Ожидаемый эффект:**
- Payment conversion: 9.3% → 40-50%
- Повторные клики: 48 → 5-10

---

## 🎯 ФАЗА 2: ONBOARDING & NAVIGATION (3-5 дней)

### ✅ ЗАДАЧА 2.1: Добавить onboarding для новых пользователей

**Приоритет:** 🟡 Важно
**Время:** 4 часа
**Цель:** Направить 64% застрявших на главном меню

#### Подзадачи:

**2.1.1. Добавить флаг "первый запуск" в БД**

**Файл:** `db/models.py`

Проверить что в модели `User` есть поле для отслеживания первого запуска:

```python
class User(Base):
    # ... существующие поля

    # Если нет этого поля — добавить:
    has_seen_onboarding: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False
    )
```

Если добавили новое поле — создать миграцию:

```bash
cd /Users/evgenijsenkevic/remnawave-tg-shop
alembic revision --autogenerate -m "Add has_seen_onboarding field"
alembic upgrade head
```

**2.1.2. Добавить ключи локализации для onboarding**

**Файл:** `locales/ru.json`

Добавить:

```json
{
  "onboarding_first_time": "Привет, {user_name}! 👋\n\nЯ помогу тебе подключить VPN за 1 минуту\n\n<b>Вот что я умею:</b>\n✅ 3 дня бесплатно\n✅ Работает с YouTube, Instagram, TikTok  \n✅ Быстрая настройка\n\nНачнём? 👇",
  "onboarding_explore_button": "Сначала посмотрю что тут есть"
}
```

**Файл:** `locales/en.json`

```json
{
  "onboarding_first_time": "Hi, {user_name}! 👋\n\nI'll help you set up VPN in 1 minute\n\n<b>What I can do:</b>\n✅ 3 days free\n✅ Works with YouTube, Instagram, TikTok  \n✅ Quick setup\n\nLet's start? 👇",
  "onboarding_explore_button": "I'll look around first"
}
```

**2.1.3. Модифицировать start handler**

**Файл:** `bot/handlers/user/start.py`

Найти функцию `start_command_handler` (строка ~305) и модифицировать:

```python
@router.message(CommandStart())
@router.message(CommandStart(magic=F.args.regexp(r"^ref_((?:[uU][A-Za-z0-9]{9})|(?:[A-Za-z0-9]{9})|\d+)$").as_("ref_match")))
@router.message(CommandStart(magic=F.args.regexp(r"^promo_(\w+)$").as_("promo_match")))
@router.message(CommandStart(magic=F.args.regexp(r"^(?!ref_|promo_)([A-Za-z0-9_\-]{2,64})$").as_("ad_param_match")))
async def start_command_handler(message: types.Message,
                                state: FSMContext,
                                settings: Settings,
                                i18n_data: dict,
                                subscription_service: SubscriptionService,
                                session: AsyncSession,
                                ref_match: Optional[re.Match] = None,
                                promo_match: Optional[re.Match] = None,
                                ad_param_match: Optional[re.Match] = None):
    await state.clear()
    current_lang = i18n_data.get("current_language", settings.DEFAULT_LANGUAGE)
    i18n: Optional[JsonI18n] = i18n_data.get("i18n_instance")
    _ = lambda key, **kwargs: i18n.gettext(current_lang, key, **kwargs) if i18n else key

    user = message.from_user
    user_id = user.id

    # ... существующий код для обработки ref_match, promo_match, ad_param_match ...

    # ... существующий код для создания/обновления пользователя ...

    db_user = await user_dal.get_user_by_id(session, user_id)

    # ✅ ДОБАВИТЬ: Проверка первого запуска
    is_first_time = False
    if db_user and not db_user.has_seen_onboarding:
        is_first_time = True

    # ... существующий код для channel subscription ...

    if not await ensure_required_channel_subscription(message, settings, i18n,
                                                      current_lang, session,
                                                      db_user):
        return

    # ✅ ДОБАВИТЬ: Показ onboarding для новых пользователей
    if is_first_time and settings.TRIAL_ENABLED and not settings.DISABLE_WELCOME_MESSAGE:
        # Показываем onboarding только если есть trial
        onboarding_text = _(
            "onboarding_first_time",
            user_name=hd.quote(user.full_name)
        )

        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton

        builder = InlineKeyboardBuilder()

        # Главная кнопка — попробовать trial
        builder.row(
            InlineKeyboardButton(
                text=_(key="menu_activate_trial_button"),
                callback_data="main_action:request_trial"
            )
        )

        # Вторая кнопка — пропустить и посмотреть меню
        builder.row(
            InlineKeyboardButton(
                text=_(key="onboarding_explore_button"),
                callback_data="main_action:skip_onboarding"
            )
        )

        await message.answer(
            onboarding_text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )

        # Отмечаем что показали onboarding
        await user_dal.update_user(session, user_id, {"has_seen_onboarding": True})

        return  # Не показываем главное меню

    # Auto-apply promo code если есть
    if promo_code_to_apply:
        # ... существующий код ...

    # Обычный flow для вернувшихся пользователей
    await send_main_menu(message,
                         settings,
                         i18n_data,
                         subscription_service,
                         session,
                         is_edit=False)
```

**2.1.4. Добавить handler для "skip_onboarding"**

**Файл:** `bot/handlers/user/start.py`

В функцию `main_action_callback_handler` (строка ~671) добавить новый action:

```python
@router.callback_query(F.data.startswith("main_action:"))
async def main_action_callback_handler(...):
    await callback.answer()

    action = callback.data.split(":")[1]
    user_id = callback.from_user.id

    # ... существующие actions ...

    # ✅ ДОБАВИТЬ новый action:
    elif action == "skip_onboarding":
        # Пользователь нажал "Сначала посмотрю что тут есть"
        await send_main_menu(callback,
                             settings,
                             i18n_data,
                             subscription_service,
                             session,
                             is_edit=True)

    # ... остальные actions ...
```

**2.1.5. Обновить метод в user_dal**

**Файл:** `db/dal/user_dal.py`

Убедиться что метод `update_user` поддерживает обновление `has_seen_onboarding`:

```python
async def update_user(
    session: AsyncSession,
    user_id: int,
    update_data: dict
) -> bool:
    """Обновить данные пользователя"""
    stmt = (
        update(User)
        .where(User.user_id == user_id)
        .values(**update_data)
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount > 0
```

**Чеклист:**
- [ ] Добавлено поле `has_seen_onboarding` в модель
- [ ] Создана и применена миграция
- [ ] Добавлены ключи локализации (ru + en)
- [ ] Модифицирован `start_command_handler`
- [ ] Добавлен handler для `skip_onboarding`
- [ ] Проверен метод `update_user`
- [ ] Протестировано на новом пользователе
- [ ] Onboarding показывается только первый раз
- [ ] После onboarding флаг устанавливается

---

### ✅ ЗАДАЧА 2.2: Оптимизировать главное меню

**Приоритет:** 🟡 Важно
**Время:** 2 часа
**Цель:** Сделать trial кнопку более заметной

#### Подзадачи:

**2.2.1. Изменить порядок кнопок в главном меню**

**Файл:** `bot/keyboards/inline/user_keyboards.py`

Найти функцию `get_main_menu_inline_keyboard` (строка ~8) и модифицировать:

```python
def get_main_menu_inline_keyboard(
        lang: str,
        i18n_instance,
        settings: Settings,
        show_trial_button: bool = False) -> InlineKeyboardMarkup:
    _ = lambda key, **kwargs: i18n_instance.gettext(lang, key, **kwargs)
    builder = InlineKeyboardBuilder()

    # ✅ ИЗМЕНИТЬ: Trial кнопка всегда первая и более заметная
    if show_trial_button and settings.TRIAL_ENABLED:
        builder.row(
            InlineKeyboardButton(
                text=_(key="menu_activate_trial_button"),
                callback_data="main_action:request_trial"
            )
        )

    # ✅ ИЗМЕНИТЬ: Subscribe и My Subscription в одной строке
    subscribe_button = InlineKeyboardButton(
        text=_(key="menu_subscribe_inline"),
        callback_data="main_action:subscribe"
    )
    my_sub_button = InlineKeyboardButton(
        text=_(key="menu_my_subscription_inline"),
        callback_data="main_action:my_subscription"
    )

    builder.row(subscribe_button, my_sub_button)

    # Referral остаётся отдельно
    referral_button = InlineKeyboardButton(
        text=_(key="menu_referral_inline"),
        callback_data="main_action:referral"
    )
    builder.row(referral_button)

    # Status button если есть
    status_button_list = []
    if settings.SERVER_STATUS_URL:
        status_button_list.append(
            InlineKeyboardButton(
                text=_(key="menu_server_status_button"),
                url=settings.SERVER_STATUS_URL
            )
        )

    if status_button_list:
        builder.row(*status_button_list)

    # Support и Terms внизу
    if settings.SUPPORT_LINK:
        builder.row(
            InlineKeyboardButton(
                text=_(key="menu_support_button"),
                url=settings.SUPPORT_LINK
            )
        )

    if settings.TERMS_OF_SERVICE_URL:
        builder.row(
            InlineKeyboardButton(
                text=_(key="menu_terms_button"),
                url=settings.TERMS_OF_SERVICE_URL
            )
        )

    return builder.as_markup()
```

**2.2.2. Обновить текст приглашения в главном меню**

Уже сделано в Задаче 1.2.2:
```json
"main_menu_greeting": "Начни с бесплатного пробного периода 👇"
```

**Чеклист:**
- [ ] Trial кнопка первая (если показывается)
- [ ] Subscribe и My Subscription в одной строке
- [ ] Порядок: Trial → Subscribe/MySub → Referral → Support → Terms
- [ ] Протестировано визуально
- [ ] Меню выглядит чище

---

### ✅ ЗАДАЧА 2.3: Добавить напоминание о неподключённом VPN

**Приоритет:** 🟡 Важно
**Время:** 3 часа
**Цель:** Увеличить конверсию "trial activated → VPN connected"

#### Подзадачи:

**2.3.1. Проверить существующий reminder в trial_handler**

**Файл:** `bot/handlers/user/trial_handler.py`

Проверить что функция `schedule_not_connected_reminder` (строка ~25) существует и работает:

```python
async def schedule_not_connected_reminder(
    bot: Bot,
    user_id: int,
    panel_user_uuid: str,
    panel_service: PanelApiService,
    settings: Settings,
    i18n,
    current_lang: str,
    connect_button_url: Optional[str] = None,
):
    """
    Background task that waits after trial activation,
    then checks if user has connected any devices.
    If not connected, sends a reminder message.
    """
    try:
        # Wait before checking (5-10 minutes)
        delay_seconds = random.randint(300, 600)
        logging.info(f"Reminder task started for user {user_id}, will check in {delay_seconds} seconds")
        await asyncio.sleep(delay_seconds)

        # Check if user connected devices
        devices_response = await panel_service.get_user_devices(panel_user_uuid)

        has_devices = False
        if devices_response:
            devices_list = devices_response.get("devices") if isinstance(devices_response, dict) else devices_response
            if isinstance(devices_list, list) and len(devices_list) > 0:
                has_devices = True

        if has_devices:
            logging.debug(f"User {user_id} has connected devices, skipping reminder")
            return

        # Send reminder
        _ = lambda key, **kwargs: i18n.gettext(current_lang, key, **kwargs) if i18n else key

        reminder_text = _("trial_not_connected_reminder")

        keyboard = None
        if connect_button_url:
            from bot.keyboards.inline.user_keyboards import get_connect_and_main_keyboard
            keyboard = get_connect_and_main_keyboard(
                current_lang,
                i18n,
                settings,
                config_link=None,
                connect_button_url=connect_button_url,
                include_support=True,
            )

        await bot.send_message(
            chat_id=user_id,
            text=reminder_text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        logging.info(f"Sent not-connected reminder to user {user_id}")

    except Exception as e:
        logging.error(f"Error in not-connected reminder for user {user_id}: {e}")
```

**2.3.2. Проверить ключ локализации**

**Файл:** `locales/ru.json`

Проверить что есть (строка ~181):

```json
{
  "trial_not_connected_reminder": "👋 Вижу, что VPN ещё не подключён.\n\nЗастрял на каком-то шаге? Напиши что не получается — помогу разобраться.\n\nИли если неудобно сейчас — можешь вернуться позже, твой бесплатный период уже активирован."
}
```

Можно улучшить:

```json
{
  "trial_not_connected_reminder": "👋 Привет! VPN ещё не подключён.\n\n💡 <b>Где застрял?</b> Напиши — помогу!\n\nИли вернись когда удобно — твои 7 дней уже активированы ✅"
}
```

**2.3.3. Убедиться что reminder запускается**

**Файл:** `bot/handlers/user/trial_handler.py`

Проверить что в `request_trial_confirmation_handler` (строка ~89) reminder запускается:

```python
# После успешной активации триала:
if activation_result and activation_result.get("activated"):
    # ... existing code ...

    # Schedule reminder (строка ~195)
    panel_user_uuid = activation_result.get("panel_user_uuid")
    if panel_user_uuid:
        logging.info(f"Scheduling not-connected reminder for user {user_id}")
        task = asyncio.create_task(
            schedule_not_connected_reminder(
                bot=callback.bot,
                user_id=user_id,
                panel_user_uuid=panel_user_uuid,
                panel_service=subscription_service.panel_service,
                settings=settings,
                i18n=i18n,
                current_lang=current_lang,
                connect_button_url=connect_button_url_for_trial,
            )
        )
        task.add_done_callback(
            lambda t: logging.error(f"Reminder task for user {user_id} failed: {t.exception()}")
            if t.exception() else None
        )
```

**Чеклист:**
- [ ] Функция `schedule_not_connected_reminder` существует
- [ ] Ключ `trial_not_connected_reminder` обновлён
- [ ] Reminder запускается после активации триала
- [ ] Протестировано (получено напоминание через 5-10 мин)
- [ ] В логах нет ошибок

---

## 📊 КОНТРОЛЬНАЯ ТОЧКА ФАЗЫ 2

После завершения всех задач Фазы 2:

**Тестирование:**
1. Создать нового пользователя (новый Telegram аккаунт)
2. Запустить /start — должен показаться onboarding
3. Проверить что onboarding показывается только раз
4. Проверить что главное меню оптимизировано
5. Активировать trial и проверить reminder

**Метрики для проверки:**
- [ ] Новые пользователи видят onboarding
- [ ] Onboarding не повторяется
- [ ] Trial кнопка заметнее остальных
- [ ] Reminder приходит через 5-10 минут

**Ожидаемый эффект:**
- Trial conversion: 9.2% → 20-25%
- Застрявших на меню: 64% → 30-35%

---

## 🎯 ФАЗА 3: ADVANCED FEATURES (5-7 дней)

### ✅ ЗАДАЧА 3.1: Внедрить deep linking для автоподключения

**Приоритет:** 🟢 Улучшение
**Время:** 8-12 часов
**Цель:** Увеличить "trial → connected" конверсию в 3-5 раз

#### Подзадачи:

**3.1.1. Изучить формат deep link для VPN приложения**

Узнать у разработчиков приложения (Hiddify, Happ, или другое) формат deep link:

Примеры:
- Hiddify: `hiddify://import/{base64_config}`
- V2rayNG: `v2rayng://install-config?url={config_url}`
- Outline: `ss://{base64_config}`

**3.1.2. Создать функцию генерации deep link**

**Файл:** `bot/utils/config_link.py`

Модифицировать функцию `prepare_config_links`:

```python
async def prepare_config_links(
    settings: Settings,
    subscription_url: Optional[str]
) -> tuple[Optional[str], Optional[str]]:
    """
    Подготовить ссылки для подключения к VPN.

    Returns:
        (config_link_display, connect_button_url)

        config_link_display: обычная ссылка для копирования
        connect_button_url: deep link для кнопки "Подключиться"
    """
    if not subscription_url:
        return None, None

    config_link_display = subscription_url

    # ✅ ДОБАВИТЬ: Генерация deep link
    connect_button_url = subscription_url

    # Если включен deep linking
    if settings.VPN_APP_DEEP_LINK_ENABLED:
        app_scheme = settings.VPN_APP_SCHEME  # например "hiddify"

        if app_scheme == "hiddify":
            # Формат: hiddify://import/{url}
            import urllib.parse
            encoded_url = urllib.parse.quote(subscription_url, safe='')
            connect_button_url = f"hiddify://import/{encoded_url}"

        elif app_scheme == "v2rayng":
            # Формат: v2rayng://install-config?url={url}
            import urllib.parse
            encoded_url = urllib.parse.quote(subscription_url, safe='')
            connect_button_url = f"v2rayng://install-config?url={encoded_url}"

        # Добавить другие схемы по необходимости

    return config_link_display, connect_button_url
```

**3.1.3. Добавить настройки в config**

**Файл:** `config/settings.py`

Добавить новые переменные окружения:

```python
class Settings(BaseSettings):
    # ... существующие настройки ...

    # Deep linking для VPN приложений
    VPN_APP_DEEP_LINK_ENABLED: bool = Field(
        default=False,
        description="Enable deep linking to VPN app"
    )

    VPN_APP_SCHEME: str = Field(
        default="hiddify",
        description="VPN app URL scheme (hiddify, v2rayng, outline, etc.)"
    )
```

**Файл:** `.env`

Добавить:

```bash
VPN_APP_DEEP_LINK_ENABLED=true
VPN_APP_SCHEME=hiddify
```

**3.1.4. Обновить клавиатуру подключения**

**Файл:** `bot/keyboards/inline/user_keyboards.py`

Функция `get_connect_and_main_keyboard` (строка ~373) уже поддерживает `connect_button_url`.

Проверить что она используется:

```python
def get_connect_and_main_keyboard(
        lang: str,
        i18n_instance,
        settings: Settings,
        config_link: Optional[str],
        connect_button_url: Optional[str] = None,
        preserve_message: bool = False,
        include_support: bool = False) -> InlineKeyboardMarkup:
    """Keyboard with a connect button and a back to main menu button."""
    _ = lambda key, **kwargs: i18n_instance.gettext(lang, key, **kwargs)
    builder = InlineKeyboardBuilder()

    # ✅ УЖЕ РЕАЛИЗОВАНО: Использование connect_button_url
    button_target = connect_button_url or config_link

    if settings.SUBSCRIPTION_MINI_APP_URL:
        builder.row(
            InlineKeyboardButton(
                text=_("connect_button"),
                web_app=WebAppInfo(url=settings.SUBSCRIPTION_MINI_APP_URL),
            )
        )
    elif button_target:
        builder.row(
            InlineKeyboardButton(text=_("connect_button"), url=button_target)
        )
    # ... rest of the code
```

**3.1.5. Добавить fallback для пользователей без приложения**

**Новый файл:** `bot/utils/app_install_links.py`

```python
"""
Ссылки для установки VPN приложений по платформам
"""

def get_app_install_link(platform: str, app_name: str = "hiddify") -> str:
    """
    Получить ссылку для установки VPN приложения.

    Args:
        platform: "ios" или "android"
        app_name: Название приложения

    Returns:
        URL для скачивания приложения
    """
    links = {
        "hiddify": {
            "ios": "https://apps.apple.com/app/hiddify/id6596777532",
            "android": "https://play.google.com/store/apps/details?id=com.hiddify.app"
        },
        "v2rayng": {
            "android": "https://play.google.com/store/apps/details?id=com.v2ray.ang"
        },
        "outline": {
            "ios": "https://apps.apple.com/app/outline-app/id1356177741",
            "android": "https://play.google.com/store/apps/details?id=org.outline.android.client"
        }
    }

    app_links = links.get(app_name, {})
    return app_links.get(platform, "")
```

**3.1.6. Добавить инструкции для установки**

**Файл:** `locales/ru.json`

Добавить:

```json
{
  "install_app_prompt": "Для подключения нужно установить приложение {app_name}\n\nВыбери свою платформу:",
  "install_ios_button": "📱 iPhone (iOS)",
  "install_android_button": "🤖 Android",
  "app_installed_question": "Приложение установлено?",
  "yes_app_installed": "✅ Да, установил",
  "install_later": "Установлю позже"
}
```

**Чеклист:**
- [ ] Изучен формат deep link для приложения
- [ ] Создана функция генерации deep link
- [ ] Добавлены настройки в config
- [ ] Обновлена клавиатура (проверено что работает)
- [ ] Добавлен fallback для установки приложения
- [ ] Добавлены ключи локализации
- [ ] Протестировано на iOS и Android
- [ ] Deep link открывает приложение автоматически

---

### ✅ ЗАДАЧА 3.2: Настроить A/B тестирование

**Приоритет:** 🟢 Улучшение
**Время:** 2-3 дня
**Цель:** Оптимизировать тексты на основе данных

#### Подзадачи:

**3.2.1. Создать модуль A/B тестирования**

**Новый файл:** `bot/utils/ab_testing.py`

```python
"""
A/B Testing framework для оптимизации конверсий
"""

import hashlib
from enum import Enum
from typing import Optional


class ABVariant(str, Enum):
    """Варианты A/B теста"""
    A = "A"
    B = "B"


class ABTest:
    """Класс для проведения A/B тестов"""

    def __init__(self, test_name: str, enabled: bool = True):
        self.test_name = test_name
        self.enabled = enabled

    def get_variant(self, user_id: int) -> ABVariant:
        """
        Определить вариант для пользователя (детерминировано).

        Использует hash user_id для стабильного распределения 50/50.
        """
        if not self.enabled:
            return ABVariant.A

        # Хеш user_id для детерминированного распределения
        hash_value = int(hashlib.md5(f"{self.test_name}:{user_id}".encode()).hexdigest(), 16)

        # 50/50 split
        return ABVariant.A if hash_value % 2 == 0 else ABVariant.B

    def get_text_variant(
        self,
        user_id: int,
        text_a: str,
        text_b: str
    ) -> str:
        """Получить текст в зависимости от варианта"""
        variant = self.get_variant(user_id)
        return text_a if variant == ABVariant.A else text_b


# Глобальные тесты
WELCOME_MESSAGE_TEST = ABTest("welcome_message_v1", enabled=False)
TRIAL_CTA_TEST = ABTest("trial_cta_v1", enabled=False)
```

**3.2.2. Добавить таблицу для отслеживания метрик**

**Файл:** `db/models.py`

Добавить новую модель:

```python
class ABTestMetric(Base):
    """Метрики A/B тестов"""
    __tablename__ = "ab_test_metrics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    test_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    variant: Mapped[str] = mapped_column(String(10), nullable=False)  # "A" or "B"
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)

    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "view", "click", "conversion"
    event_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        Index("idx_ab_test_name_variant", "test_name", "variant"),
        Index("idx_ab_user_test", "user_id", "test_name"),
    )
```

Создать миграцию:

```bash
alembic revision --autogenerate -m "Add AB test metrics table"
alembic upgrade head
```

**3.2.3. Создать DAL для A/B метрик**

**Новый файл:** `db/dal/ab_test_dal.py`

```python
"""Data Access Layer for A/B testing metrics"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timezone
from typing import Optional

from db.models import ABTestMetric


async def track_ab_event(
    session: AsyncSession,
    test_name: str,
    variant: str,
    user_id: int,
    event_type: str,
    event_data: Optional[dict] = None
):
    """Записать событие A/B теста"""
    metric = ABTestMetric(
        test_name=test_name,
        variant=variant,
        user_id=user_id,
        event_type=event_type,
        event_data=event_data,
        created_at=datetime.now(timezone.utc)
    )
    session.add(metric)
    await session.commit()


async def get_ab_test_stats(
    session: AsyncSession,
    test_name: str
) -> dict:
    """
    Получить статистику A/B теста.

    Returns:
        {
            "A": {"views": 100, "clicks": 50, "conversions": 10},
            "B": {"views": 100, "clicks": 60, "conversions": 15}
        }
    """
    stmt = (
        select(
            ABTestMetric.variant,
            ABTestMetric.event_type,
            func.count(ABTestMetric.id).label("count")
        )
        .where(ABTestMetric.test_name == test_name)
        .group_by(ABTestMetric.variant, ABTestMetric.event_type)
    )

    result = await session.execute(stmt)
    rows = result.all()

    stats = {"A": {}, "B": {}}

    for variant, event_type, count in rows:
        if variant not in stats:
            stats[variant] = {}
        stats[variant][event_type] = count

    return stats
```

**3.2.4. Интегрировать A/B тест в приветствие**

**Файл:** `bot/handlers/user/start.py`

Пример использования:

```python
from bot.utils.ab_testing import WELCOME_MESSAGE_TEST
from db.dal import ab_test_dal

async def start_command_handler(...):
    # ... existing code ...

    # A/B тест приветственного сообщения
    welcome_text_a = _("welcome", user_name=hd.quote(user.full_name))
    welcome_text_b = _("welcome_variant_b", user_name=hd.quote(user.full_name))

    variant = WELCOME_MESSAGE_TEST.get_variant(user_id)
    welcome_text = WELCOME_MESSAGE_TEST.get_text_variant(
        user_id,
        welcome_text_a,
        welcome_text_b
    )

    # Трекинг view
    if WELCOME_MESSAGE_TEST.enabled:
        await ab_test_dal.track_ab_event(
            session=session,
            test_name="welcome_message_v1",
            variant=variant.value,
            user_id=user_id,
            event_type="view"
        )

    await message.answer(welcome_text)
```

**3.2.5. Создать админ команду для просмотра статистики**

**Файл:** `bot/handlers/admin/ab_testing.py` (новый)

```python
"""Admin handlers for A/B testing"""

from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from db.dal import ab_test_dal

router = Router(name="admin_ab_testing_router")


@router.message(Command("ab_stats"))
async def show_ab_stats(message: types.Message, session: AsyncSession):
    """Показать статистику A/B тестов (только для админов)"""

    # Получить статистику для всех активных тестов
    tests = ["welcome_message_v1", "trial_cta_v1"]

    response = "📊 <b>Статистика A/B тестов</b>\n\n"

    for test_name in tests:
        stats = await ab_test_dal.get_ab_test_stats(session, test_name)

        response += f"<b>{test_name}</b>\n"

        for variant in ["A", "B"]:
            variant_stats = stats.get(variant, {})
            views = variant_stats.get("view", 0)
            clicks = variant_stats.get("click", 0)
            conversions = variant_stats.get("conversion", 0)

            ctr = (clicks / views * 100) if views > 0 else 0
            cvr = (conversions / views * 100) if views > 0 else 0

            response += f"  Вариант {variant}:\n"
            response += f"    👁 Views: {views}\n"
            response += f"    👆 Clicks: {clicks} ({ctr:.1f}%)\n"
            response += f"    ✅ Conversions: {conversions} ({cvr:.1f}%)\n"

        response += "\n"

    await message.answer(response, parse_mode="HTML")
```

Добавить роутер в `bot/routers.py`:

```python
from bot.handlers.admin import ab_testing

# В функции build_root_router:
admin_main_router.include_router(ab_testing.router)
```

**Чеклист:**
- [ ] Создан модуль `ab_testing.py`
- [ ] Добавлена модель `ABTestMetric`
- [ ] Создана миграция
- [ ] Создан `ab_test_dal.py`
- [ ] Интегрирован A/B тест (пример)
- [ ] Создана админ команда `/ab_stats`
- [ ] Протестировано на локальном боте
- [ ] Статистика отображается корректно

---

### ✅ ЗАДАЧА 3.3: Добавить эмоциональный микрокопи

**Приоритет:** 🟢 Улучшение
**Время:** 2 часа
**Цель:** Повысить эмоциональную связь с пользователем

#### Подзадачи:

**3.3.1. Обновить все success сообщения**

**Файл:** `locales/ru.json`

Найти и заменить:

```json
{
  // Payment success
  "payment_successful_full": "🎉 Спасибо! Подписка оформлена ❤️\n\n✅ Активна до {end_date}\n\nТеперь подключимся — это займёт минуту 👇",

  "payment_successful_traffic_full": "🎉 Отлично! Пакет активирован ❤️\n\n📊 Трафик: {traffic_gb} ГБ\n✅ Действует до {end_date}\n\nПодключаемся 👇",

  // Trial success
  "trial_activated_alert": "Ура! 🎉 Твой бесплатный VPN активирован!",

  // Promo success
  "promo_code_applied_success_full": "🎉 Промокод сработал!\n\n✅ Подписка активна до {end_date}\n\nТеперь подключимся 👇",

  // Referral bonus
  "referral_bonus_inviter_notification_extended": "🎉 Отличная новость! Твой друг {referee_name} оплатил подписку. Тебе начислено {days} бонусных дней! ❤️\n\nТеперь подписка активна до {new_end_date}",

  "referral_bonus_inviter_notification_new_sub": "🎉 Ура! Твой друг {referee_name} оплатил подписку. Тебе подарок — {days} дней VPN! ❤️\n\nАктивна до {new_end_date}"
}
```

**3.3.2. Улучшить error сообщения**

Уже сделано в Задаче 1.2.4, но можно дополнить:

```json
{
  "payment_failed": "😔 Оплата не прошла\n\nПопробуй ещё раз или выбери другой способ.\n\nЕсли нужна помощь — напиши нам 👉 @Forours_Helper",

  "trial_feature_disabled": "😔 Пробный период сейчас недоступен\n\nНо можешь сразу оформить подписку — первый месяц всего 99₽!",

  "subscription_not_active": "У тебя пока нет активной подписки 😔\n\nНо это легко исправить! Выбери тариф 👇"
}
```

**3.3.3. Добавить эмодзи в кнопки (опционально)**

Кнопки уже имеют эмодзи, но можно добавить больше эмоций:

```json
{
  "connect_button": "🚀 Подключиться сейчас",
  "back_to_main_menu_button": "⬅️ Вернуться в меню",
  "cancel_button": "❌ Отменить"
}
```

**Чеклист:**
- [ ] Обновлены все success сообщения
- [ ] Улучшены error сообщения
- [ ] Добавлены эмодзи где уместно
- [ ] Протестировано на пользователях
- [ ] Тексты звучат дружелюбно

---

## 📊 КОНТРОЛЬНАЯ ТОЧКА ФАЗЫ 3

После завершения всех задач Фазы 3:

**Тестирование:**
1. Проверить deep linking на iOS и Android
2. Запустить A/B тест на 100 пользователях
3. Проверить статистику через `/ab_stats`
4. Убедиться что все тексты дружелюбные

**Метрики для проверки:**
- [ ] Deep link открывает приложение автоматически
- [ ] A/B тесты собирают метрики
- [ ] Админ видит статистику
- [ ] Тексты вызывают положительные эмоции

**Ожидаемый эффект:**
- Final conversion: 3-5% → 25-35%
- Churn: снижение на 15-20%

---

## 🎯 ФИНАЛЬНАЯ ПРОВЕРКА

### Чеклист всех изменений:

**Фаза 1: Quick Wins**
- [ ] ✅ Задача 1.1: Feedback на кнопки
- [ ] ✅ Задача 1.2: Обновление текстов
- [ ] ✅ Задача 1.3: Удаление reply keyboard
- [ ] ✅ Задача 1.4: Статусы оплаты

**Фаза 2: Onboarding & Navigation**
- [ ] ✅ Задача 2.1: Onboarding для новых
- [ ] ✅ Задача 2.2: Оптимизация меню
- [ ] ✅ Задача 2.3: Reminder о подключении

**Фаза 3: Advanced Features**
- [ ] ✅ Задача 3.1: Deep linking
- [ ] ✅ Задача 3.2: A/B тестирование
- [ ] ✅ Задача 3.3: Эмоциональный копирайт

---

## 📈 ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ

| Метрика | До | После | Прирост |
|---------|----|----|---------|
| **Trial conversion** | 9.2% | 25-30% | **+170-225%** |
| **Payment conversion** | 9.3% | 50-60% | **+440-545%** |
| **Застрявших на меню** | 64% | 25-30% | **-53-61%** |
| **Повторные клики** | 48 | 5-10 | **-79-90%** |
| **Final conversion** | 3-5% | 25-35% | **+400-700%** |

---

## 🚀 ДЕПЛОЙ

После завершения всех задач:

1. **Код ревью** всех изменений
2. **Тестирование** на staging окружении
3. **Миграции БД** на production
4. **Постепенный rollout** (10% → 50% → 100% пользователей)
5. **Мониторинг метрик** первые 48 часов
6. **Сбор feedback** от пользователей

---

**Конец плана задач**

Общее время: **10-12 дней**
Общий ожидаемый прирост конверсии: **+400-700%**
