from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.lang_kb import get_lang_keyboard
from keyboards.main_menu import get_main_menu
from models.user import User
from database.connection import async_session_maker
from database.repositories.user_repo import UserRepository

router = Router()

WELCOME_TEXTS = {
    "uz": (
        "Salom, <b>{name}</b>! 👋\n\n"
        "<b>ZIYRAK AI</b> ga xush kelibsiz!\n\n"
        "Men sizning aqlli hayot maslahatchingizman:\n"
        "• Huquqiy vaziyatlar\n"
        "• Biznes masalalari\n"
        "• Hujjat tayyorlash\n"
        "• Moliyaviy maslahat\n\n"
        "Tilni tanlang 👇"
    ),
    "ru": (
        "Привет, <b>{name}</b>! 👋\n\n"
        "Добро пожаловать в <b>ZIYRAK AI</b>!\n\n"
        "Я ваш умный жизненный советник:\n"
        "• Юридические ситуации\n"
        "• Бизнес вопросы\n"
        "• Составление документов\n"
        "• Финансовые советы\n\n"
        "Выберите язык 👇"
    ),
    "en": (
        "Hello, <b>{name}</b>! 👋\n\n"
        "Welcome to <b>ZIYRAK AI</b>!\n\n"
        "I am your intelligent life advisor:\n"
        "• Legal situations\n"
        "• Business questions\n"
        "• Document preparation\n"
        "• Financial advice\n\n"
        "Choose language 👇"
    ),
    "tr": (
        "Merhaba, <b>{name}</b>! 👋\n\n"
        "<b>ZIYRAK AI</b>'a hoş geldiniz!\n\n"
        "Ben sizin akıllı yaşam danışmanınızım.\n\n"
        "Dil seçin 👇"
    ),
    "ar": (
        "مرحبا، <b>{name}</b>! 👋\n\n"
        "مرحبًا بك في <b>ZIYRAK AI</b>!\n\n"
        "أنا مستشارك الذكي في الحياة.\n\n"
        "اختر اللغة 👇"
    ),
}

MENU_TEXTS = {
    "uz": "Asosiy menyu 👇",
    "ru": "Главное меню 👇",
    "en": "Main menu 👇",
    "tr": "Ana menü 👇",
    "ar": "القائمة الرئيسية 👇",
}

LANG_CHANGED = {
    "uz": "✅ Til o'zgartirildi: <b>O'zbek</b>\n\n",
    "ru": "✅ Язык изменён: <b>Русский</b>\n\n",
    "en": "✅ Language changed: <b>English</b>\n\n",
    "tr": "✅ Dil değiştirildi: <b>Türkçe</b>\n\n",
    "ar": "✅ تم تغيير اللغة: <b>العربية</b>\n\n",
}


@router.message(CommandStart())
async def cmd_start(message: Message, db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"

    # Agar foydalanuvchi tili allaqachon saqlangan bo'lsa
    if db_user and db_user.lang_code and db_user.lang_code != "uz":
        # To'g'ridan menyuga o'tish
        text = WELCOME_TEXTS.get(lang, WELCOME_TEXTS["uz"])
        await message.answer(
            text.format(name=message.from_user.first_name),
            reply_markup=get_lang_keyboard(),
        )
    else:
        # Yangi foydalanuvchi — til tanlash
        text = WELCOME_TEXTS.get("uz", WELCOME_TEXTS["uz"])
        await message.answer(
            text.format(name=message.from_user.first_name),
            reply_markup=get_lang_keyboard(),
        )


@router.callback_query(F.data.startswith("lang:"))
async def set_language(callback: CallbackQuery, db_user: User = None):
    lang = callback.data.split(":")[1]

    # Tanlangan tilni databasega saqlash
    async with async_session_maker() as session:
        repo = UserRepository(session)
        await repo.update_language(callback.from_user.id, lang)
        await session.commit()

    # Xabar va menyu
    changed_text = LANG_CHANGED.get(lang, LANG_CHANGED["uz"])
    menu_text = MENU_TEXTS.get(lang, MENU_TEXTS["uz"])

    await callback.message.edit_text(
        changed_text + menu_text,
        reply_markup=get_main_menu(lang),
    )
    await callback.answer()


@router.message(Command("menu"))
async def cmd_menu(message: Message, db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    menu_text = MENU_TEXTS.get(lang, MENU_TEXTS["uz"])
    await message.answer(
        menu_text,
        reply_markup=get_main_menu(lang),
    )


@router.callback_query(F.data == "menu:main")
async def main_menu_callback(callback: CallbackQuery, db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    menu_text = MENU_TEXTS.get(lang, MENU_TEXTS["uz"])
    await callback.message.answer(
        menu_text,
        reply_markup=get_main_menu(lang),
    )
    await callback.answer()