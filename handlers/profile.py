from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from models.user import User
from database.connection import async_session_maker
from database.repositories.user_repo import UserRepository

router = Router()

TEXTS = {
    "uz": {
        "title": "👤 Mening Profilim",
        "name": "Ism",
        "username": "Username",
        "lang": "Til",
        "plan": "Tarif",
        "requests": "Bugungi so'rovlar",
        "member_since": "A'zo bo'lgan",
        "free": "Bepul",
        "pro": "Pro",
        "change_lang": "🌐 Tilni o'zgartirish",
        "back": "🏠 Asosiy menyu",
        "no_username": "Yo'q",
        "langs": {
            "uz": "O'zbek",
            "ru": "Русский",
            "en": "English",
            "tr": "Türkçe",
            "ar": "العربية",
        },
    },
    "ru": {
        "title": "👤 Мой Профиль",
        "name": "Имя",
        "username": "Username",
        "lang": "Язык",
        "plan": "Тариф",
        "requests": "Запросов сегодня",
        "member_since": "Участник с",
        "free": "Бесплатный",
        "pro": "Pro",
        "change_lang": "🌐 Изменить язык",
        "back": "🏠 Главное меню",
        "no_username": "Нет",
        "langs": {
            "uz": "O'zbek",
            "ru": "Русский",
            "en": "English",
            "tr": "Türkçe",
            "ar": "العربية",
        },
    },
    "en": {
        "title": "👤 My Profile",
        "name": "Name",
        "username": "Username",
        "lang": "Language",
        "plan": "Plan",
        "requests": "Today's requests",
        "member_since": "Member since",
        "free": "Free",
        "pro": "Pro",
        "change_lang": "🌐 Change language",
        "back": "🏠 Main menu",
        "no_username": "None",
        "langs": {
            "uz": "O'zbek",
            "ru": "Русский",
            "en": "English",
            "tr": "Türkçe",
            "ar": "العربية",
        },
    },
    "tr": {
        "title": "👤 Profilim",
        "name": "İsim",
        "username": "Kullanici adi",
        "lang": "Dil",
        "plan": "Plan",
        "requests": "Bugunki istekler",
        "member_since": "Uye oldu",
        "free": "Ucretsiz",
        "pro": "Pro",
        "change_lang": "🌐 Dil degistir",
        "back": "🏠 Ana menu",
        "no_username": "Yok",
        "langs": {
            "uz": "O'zbek",
            "ru": "Русский",
            "en": "English",
            "tr": "Türkçe",
            "ar": "العربية",
        },
    },
    "ar": {
        "title": "👤 ملفي الشخصي",
        "name": "الاسم",
        "username": "اسم المستخدم",
        "lang": "اللغة",
        "plan": "الخطة",
        "requests": "طلبات اليوم",
        "member_since": "عضو منذ",
        "free": "مجاني",
        "pro": "Pro",
        "change_lang": "🌐 تغيير اللغة",
        "back": "🏠 القائمة الرئيسية",
        "no_username": "لا يوجد",
        "langs": {
            "uz": "O'zbek",
            "ru": "Русский",
            "en": "English",
            "tr": "Türkçe",
            "ar": "العربية",
        },
    },
}


def get_profile_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    t = TEXTS.get(lang, TEXTS["uz"])
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=t["change_lang"],
                callback_data="profile:change_lang"
            ),
        ],
        [
            InlineKeyboardButton(
                text=t["back"],
                callback_data="menu:main"
            ),
        ],
    ])


def get_lang_change_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang:uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
        ],
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="lang:tr"),
        ],
        [
            InlineKeyboardButton(text="🇸🇦 العربية", callback_data="lang:ar"),
        ],
    ])


def build_profile_text(user: User, lang: str) -> str:
    t = TEXTS.get(lang, TEXTS["uz"])

    username = f"@{user.username}" if user.username else t["no_username"]
    lang_name = t["langs"].get(user.lang_code, user.lang_code)
    plan_name = t["pro"] if user.plan == "pro" else t["free"]

    created = user.created_at.strftime("%d.%m.%Y") if user.created_at else "—"

    text = (
        f"<b>{t['title']}</b>\n\n"
        f"👤 <b>{t['name']}:</b> {user.full_name or '—'}\n"
        f"🔗 <b>{t['username']}:</b> {username}\n"
        f"🌐 <b>{t['lang']}:</b> {lang_name}\n"
        f"⭐ <b>{t['plan']}:</b> {plan_name}\n"
        f"📊 <b>{t['requests']}:</b> {user.daily_requests_used}\n"
        f"📅 <b>{t['member_since']}:</b> {created}\n"
    )
    return text


@router.message(Command("profile"))
async def cmd_profile(message: Message, db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    text = build_profile_text(db_user, lang)
    await message.answer(
        text,
        reply_markup=get_profile_keyboard(lang)
    )


@router.callback_query(F.data == "menu:profile")
async def profile_callback(callback: CallbackQuery, db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    text = build_profile_text(db_user, lang)
    await callback.message.answer(
        text,
        reply_markup=get_profile_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "profile:change_lang")
async def change_lang_callback(callback: CallbackQuery):
    await callback.message.answer(
        "🌐 Tilni tanlang / Выберите язык / Choose language:",
        reply_markup=get_lang_change_keyboard()
    )
    await callback.answer()
