from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_lang_keyboard() -> InlineKeyboardMarkup:
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