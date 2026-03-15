from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from keyboards.lang_kb import get_lang_keyboard
from keyboards.main_menu import get_main_menu
from models.user import User

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
        "Выберите язык 👇"
    ),
    "en": (
        "Hello, <b>{name}</b>! 👋\n\n"
        "Welcome to <b>ZIYRAK AI</b>!\n\n"
        "Choose language 👇"
    ),
}


@router.message(CommandStart())
async def cmd_start(message: Message, db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    text = WELCOME_TEXTS.get(lang, WELCOME_TEXTS["uz"])
    await message.answer(
        text.format(name=message.from_user.first_name),
        reply_markup=get_lang_keyboard(),
    )


@router.callback_query(F.data.startswith("lang:"))
async def set_language(callback: CallbackQuery, db_user: User = None):
    lang = callback.data.split(":")[1]
    lang_names = {
        "uz": "O'zbek", "ru": "Русский",
        "en": "English", "tr": "Türkçe", "ar": "العربية"
    }
    await callback.message.edit_text(
        f"✅ Til tanlandi: <b>{lang_names.get(lang, lang)}</b>\n\n"
        f"Asosiy menyu 👇",
        reply_markup=get_main_menu(lang),
    )
    await callback.answer()


@router.message(Command("menu"))
async def cmd_menu(message: Message, db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    await message.answer(
        "Asosiy menyu 👇",
        reply_markup=get_main_menu(lang),
    )