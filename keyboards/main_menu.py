from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

MENU_TEXTS = {
    "uz": {
        "situation": "🧠 Vaziyat Yechimi",
        "document": "📄 Hujjat Yarat",
        "expert": "👨‍⚖️ Ekspert",
        "profile": "👤 Profilim",
        "settings": "⚙️ Sozlamalar",
        "premium": "⭐ Premium",
    },
    "ru": {
        "situation": "🧠 Решить ситуацию",
        "document": "📄 Создать документ",
        "expert": "👨‍⚖️ Эксперт",
        "profile": "👤 Мой профиль",
        "settings": "⚙️ Настройки",
        "premium": "⭐ Премиум",
    },
    "en": {
        "situation": "🧠 Solve Situation",
        "document": "📄 Create Document",
        "expert": "👨‍⚖️ Expert",
        "profile": "👤 My Profile",
        "settings": "⚙️ Settings",
        "premium": "⭐ Premium",
    },
}


def get_main_menu(lang: str = "uz") -> InlineKeyboardMarkup:
    t = MENU_TEXTS.get(lang, MENU_TEXTS["uz"])
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t["situation"], callback_data="menu:situation"),
            InlineKeyboardButton(text=t["document"], callback_data="menu:document"),
        ],
        [
            InlineKeyboardButton(text=t["expert"], callback_data="menu:expert"),
            InlineKeyboardButton(text=t["profile"], callback_data="menu:profile"),
        ],
        [
            InlineKeyboardButton(text="👥 Referral", callback_data="menu:referral"),
            InlineKeyboardButton(text=t["settings"], callback_data="menu:settings"),
        ],
        [
            InlineKeyboardButton(text=t["premium"], callback_data="menu:premium"),
        ],
    ])