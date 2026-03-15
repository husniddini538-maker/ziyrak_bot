from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

from models.user import User
from database.connection import async_session_maker

router = Router()

PLANS = {
    "1month": {"price_uzs": 75000, "price_usd": 6, "months": 1, "label": "1 oy"},
    "3month": {"price_uzs": 200000, "price_usd": 16, "months": 3, "label": "3 oy"},
    "12month": {"price_uzs": 600000, "price_usd": 48, "months": 12, "label": "1 yil"},
}

TEXTS = {
    "uz": {
        "title": "<b>Premium Tarif</b>",
        "features": (
            "Premium imkoniyatlar:\n"
            "Cheksiz so'rovlar\n"
            "Barcha hujjat turlari\n"
            "Ovozli so'rov\n"
            "Ekspert bilan bog'lanish\n"
            "Ustunlik qo'llab-quvvatlash"
        ),
        "choose_plan": "Tarifni tanlang:",
        "choose_payment": "To'lov usulini tanlang:",
        "payme": "Payme orqali to'lash",
        "click": "Click orqali to'lash",
        "back": "Orqaga",
        "main_menu": "Asosiy menyu",
        "already_pro": "Siz allaqachon Premium foydalanuvchisiz!",
        "payment_info": (
            "To'lov ma'lumotlari:\n\n"
            "Tarif: {plan}\n"
            "Narx: {price} so'm\n"
            "Muddati: {months} oy\n\n"
            "To'lov usulini tanlang:"
        ),
        "payme_instruction": (
            "Payme orqali to'lash:\n\n"
            "Miqdor: {amount} so'm\n\n"
            "To'lov amalga oshirilgandan so'ng\n"
            "/check_payment buyrug'ini yuboring."
        ),
        "click_instruction": (
            "Click orqali to'lash:\n\n"
            "Miqdor: {amount} so'm\n\n"
            "To'lov amalga oshirilgandan so'ng\n"
            "/check_payment buyrug'ini yuboring."
        ),
        "activated": (
            "Premium tarif aktivlashtirildi!\n\n"
            "Davri: {months} oy\n"
            "Barcha Premium imkoniyatlar ochiq!"
        ),
        "manual_check": (
            "To'lovingiz tekshirilmoqda.\n"
            "Iltimos, 5-10 daqiqa kuting.\n"
            "Savol bo'lsa admin bilan bog'laning."
        ),
    },
    "ru": {
        "title": "<b>Премиум Тариф</b>",
        "features": (
            "Премиум возможности:\n"
            "Неограниченные запросы\n"
            "Все типы документов\n"
            "Голосовые запросы\n"
            "Связь с экспертом\n"
            "Приоритетная поддержка"
        ),
        "choose_plan": "Выберите тариф:",
        "choose_payment": "Выберите способ оплаты:",
        "payme": "Оплатить через Payme",
        "click": "Оплатить через Click",
        "back": "Назад",
        "main_menu": "Главное меню",
        "already_pro": "Вы уже Premium пользователь!",
        "payment_info": (
            "Информация об оплате:\n\n"
            "Тариф: {plan}\n"
            "Цена: {price} сум\n"
            "Срок: {months} мес.\n\n"
            "Выберите способ оплаты:"
        ),
        "payme_instruction": (
            "Оплата через Payme:\n\n"
            "Сумма: {amount} сум\n\n"
            "После оплаты отправьте /check_payment"
        ),
        "click_instruction": (
            "Оплата через Click:\n\n"
            "Сумма: {amount} сум\n\n"
            "После оплаты отправьте /check_payment"
        ),
        "activated": (
            "Премиум тариф активирован!\n\n"
            "Срок: {months} мес.\n"
            "Все Premium возможности открыты!"
        ),
        "manual_check": (
            "Ваш платёж проверяется.\n"
            "Пожалуйста, подождите 5-10 минут."
        ),
    },
    "en": {
        "title": "<b>Premium Plan</b>",
        "features": (
            "Premium features:\n"
            "Unlimited requests\n"
            "All document types\n"
            "Voice requests\n"
            "Expert connection\n"
            "Priority support"
        ),
        "choose_plan": "Choose plan:",
        "choose_payment": "Choose payment method:",
        "payme": "Pay via Payme",
        "click": "Pay via Click",
        "back": "Back",
        "main_menu": "Main menu",
        "already_pro": "You are already a Premium user!",
        "payment_info": (
            "Payment details:\n\n"
            "Plan: {plan}\n"
            "Price: {price} UZS\n"
            "Duration: {months} months\n\n"
            "Choose payment method:"
        ),
        "payme_instruction": (
            "Payment via Payme:\n\n"
            "Amount: {amount} UZS\n\n"
            "After payment send /check_payment"
        ),
        "click_instruction": (
            "Payment via Click:\n\n"
            "Amount: {amount} UZS\n\n"
            "After payment send /check_payment"
        ),
        "activated": (
            "Premium plan activated!\n\n"
            "Duration: {months} months\n"
            "All Premium features are now open!"
        ),
        "manual_check": (
            "Your payment is being verified.\n"
            "Please wait 5-10 minutes."
        ),
    },
}


def get_plans_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="1 oy — 75,000 so'm",
                callback_data="plan:1month"
            ),
        ],
        [
            InlineKeyboardButton(
                text="3 oy — 200,000 so'm",
                callback_data="plan:3month"
            ),
        ],
        [
            InlineKeyboardButton(
                text="1 yil — 600,000 so'm",
                callback_data="plan:12month"
            ),
        ],
        [
            InlineKeyboardButton(text="Orqaga", callback_data="menu:main"),
        ],
    ])


def get_payment_keyboard(plan_key: str, lang: str = "uz") -> InlineKeyboardMarkup:
    t = TEXTS.get(lang, TEXTS["uz"])
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=t["payme"],
                callback_data=f"pay:payme:{plan_key}"
            ),
        ],
        [
            InlineKeyboardButton(
                text=t["click"],
                callback_data=f"pay:click:{plan_key}"
            ),
        ],
        [
            InlineKeyboardButton(text=t["back"], callback_data="menu:premium"),
        ],
    ])


def get_after_payment_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="To'lovni tekshirish",
                callback_data="pay:check"
            ),
        ],
        [
            InlineKeyboardButton(text="Asosiy menyu", callback_data="menu:main"),
        ],
    ])


@router.message(Command("premium"))
async def cmd_premium(message: Message, db_user: User = None):
    await show_premium(message, db_user, is_callback=False)


@router.callback_query(F.data == "menu:premium")
async def premium_callback(callback: CallbackQuery, db_user: User = None):
    await show_premium(callback.message, db_user, is_callback=True)
    await callback.answer()


async def show_premium(message, db_user: User, is_callback: bool = False):
    lang = db_user.lang_code if db_user else "uz"
    t = TEXTS.get(lang, TEXTS["uz"])

    if db_user and db_user.plan == "pro":
        text = t["already_pro"]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t["main_menu"], callback_data="menu:main")]
        ])
    else:
        text = t["title"] + "\n\n" + t["features"] + "\n\n" + t["choose_plan"]
        keyboard = get_plans_keyboard(lang)

    if is_callback:
        await message.answer(text, reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("plan:"))
async def plan_chosen(callback: CallbackQuery, db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    t = TEXTS.get(lang, TEXTS["uz"])
    plan_key = callback.data.split(":")[1]
    plan = PLANS.get(plan_key, PLANS["1month"])

    text = t["payment_info"].format(
        plan=plan["label"],
        price=f"{plan['price_uzs']:,}",
        months=plan["months"]
    )

    await callback.message.answer(
        text,
        reply_markup=get_payment_keyboard(plan_key, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay:payme:"))
async def pay_payme(callback: CallbackQuery, db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    t = TEXTS.get(lang, TEXTS["uz"])
    plan_key = callback.data.split(":")[2]
    plan = PLANS.get(plan_key, PLANS["1month"])

    from models.payment import Payment
    async with async_session_maker() as session:
        payment = Payment(
            telegram_id=db_user.telegram_id,
            amount=plan["price_uzs"],
            currency="UZS",
            provider="payme",
            plan="pro",
            months=str(plan["months"]),
            status="pending",
        )
        session.add(payment)
        await session.commit()

    payme_url = f"https://payme.uz/checkout/{payment.id}"

    text = t["payme_instruction"].format(amount=f"{plan['price_uzs']:,}")

    await callback.message.answer(
        text + f"\n\nTo'lov havolasi:\n{payme_url}",
        reply_markup=get_after_payment_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay:click:"))
async def pay_click(callback: CallbackQuery, db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    t = TEXTS.get(lang, TEXTS["uz"])
    plan_key = callback.data.split(":")[2]
    plan = PLANS.get(plan_key, PLANS["1month"])

    from models.payment import Payment
    async with async_session_maker() as session:
        payment = Payment(
            telegram_id=db_user.telegram_id,
            amount=plan["price_uzs"],
            currency="UZS",
            provider="click",
            plan="pro",
            months=str(plan["months"]),
            status="pending",
        )
        session.add(payment)
        await session.commit()

    click_url = f"https://my.click.uz/services/pay?service_id=YOUR_SERVICE_ID&merchant_id=YOUR_MERCHANT_ID&amount={plan['price_uzs']}&transaction_param={payment.id}"

    text = t["click_instruction"].format(amount=f"{plan['price_uzs']:,}")

    await callback.message.answer(
        text + f"\n\nTo'lov havolasi:\n{click_url}",
        reply_markup=get_after_payment_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "pay:check")
async def check_payment(callback: CallbackQuery, db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    t = TEXTS.get(lang, TEXTS["uz"])
    await callback.message.answer(t["manual_check"])
    await callback.answer()


@router.message(Command("activate"))
async def cmd_activate(message: Message, db_user: User = None):
    from config.settings import settings
    if message.from_user.id not in settings.admin_ids_list:
        await message.answer("Ruxsat yoq!")
        return

    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Format: /activate USER_ID MONTHS\nMasalan: /activate 123456789 1")
        return

    try:
        user_id = int(parts[1])
        months = int(parts[2])
    except ValueError:
        await message.answer("Noto'g'ri format!")
        return

    from sqlalchemy import select, update
    from models.user import User as UserModel
    async with async_session_maker() as session:
        result = await session.execute(
            select(UserModel).where(UserModel.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            await message.answer(f"Foydalanuvchi topilmadi: {user_id}")
            return

        await session.execute(
            update(UserModel)
            .where(UserModel.telegram_id == user_id)
            .values(plan="pro")
        )
        await session.commit()

    try:
        await message.bot.send_message(
            chat_id=user_id,
            text=(
                "Premium tarif aktivlashtirildi!\n\n"
                f"Davri: {months} oy\n"
                "Barcha Premium imkoniyatlar ochiq!"
            )
        )
    except Exception:
        pass

    await message.answer(
        f"Premium aktivlashtirildi!\n"
        f"Foydalanuvchi: {user_id}\n"
        f"Davri: {months} oy"
    )


@router.message(Command("check_payment"))
async def user_check_payment(message: Message, db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    t = TEXTS.get(lang, TEXTS["uz"])
    await message.answer(t["manual_check"])
