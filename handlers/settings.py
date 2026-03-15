from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from models.user import User
from database.connection import async_session_maker
from database.repositories.user_repo import UserRepository

router = Router()

class DeleteStates(StatesGroup):
    confirm_delete = State()

TEXTS = {
    "uz": {
        "title": "<b>Sozlamalar</b>",
        "notifications_on": "Bildirishnomalar: Yoqilgan",
        "notifications_off": "Bildirishnomalar: O'chirilgan",
        "toggle_notif": "Bildirishnomalarni o'zgartirish",
        "change_lang": "Tilni o'zgartirish",
        "delete_account": "Hisobni o'chirish",
        "back": "Asosiy menyu",
        "notif_enabled": "Bildirishnomalar yoqildi!",
        "notif_disabled": "Bildirishnomalar o'chirildi!",
        "delete_warning": (
            "<b>Hisobni o'chirish</b>\n\n"
            "Diqqat! Bu amal qaytarib bo'lmaydi.\n"
            "Barcha ma'lumotlaringiz o'chiriladi:\n"
            "- Profil\n"
            "- So'rovlar tarixi\n"
            "- Hujjatlar\n\n"
            "Davom etasizmi?"
        ),
        "delete_confirm": "Ha, o'chirish",
        "delete_cancel": "Yo'q, bekor qilish",
        "deleted": (
            "Hisobingiz o'chirildi.\n"
            "ZIYRAK AI dan foydalanganingiz uchun rahmat!"
        ),
        "lang_title": "Tilni tanlang:",
    },
    "ru": {
        "title": "<b>Настройки</b>",
        "notifications_on": "Уведомления: Включены",
        "notifications_off": "Уведомления: Выключены",
        "toggle_notif": "Переключить уведомления",
        "change_lang": "Изменить язык",
        "delete_account": "Удалить аккаунт",
        "back": "Главное меню",
        "notif_enabled": "Уведомления включены!",
        "notif_disabled": "Уведомления выключены!",
        "delete_warning": (
            "<b>Удаление аккаунта</b>\n\n"
            "Внимание! Это действие необратимо.\n"
            "Все ваши данные будут удалены:\n"
            "- Профиль\n"
            "- История запросов\n"
            "- Документы\n\n"
            "Продолжить?"
        ),
        "delete_confirm": "Да, удалить",
        "delete_cancel": "Нет, отмена",
        "deleted": (
            "Ваш аккаунт удалён.\n"
            "Спасибо за использование ZIYRAK AI!"
        ),
        "lang_title": "Выберите язык:",
    },
    "en": {
        "title": "<b>Settings</b>",
        "notifications_on": "Notifications: Enabled",
        "notifications_off": "Notifications: Disabled",
        "toggle_notif": "Toggle notifications",
        "change_lang": "Change language",
        "delete_account": "Delete account",
        "back": "Main menu",
        "notif_enabled": "Notifications enabled!",
        "notif_disabled": "Notifications disabled!",
        "delete_warning": (
            "<b>Delete Account</b>\n\n"
            "Warning! This action is irreversible.\n"
            "All your data will be deleted:\n"
            "- Profile\n"
            "- Request history\n"
            "- Documents\n\n"
            "Continue?"
        ),
        "delete_confirm": "Yes, delete",
        "delete_cancel": "No, cancel",
        "deleted": (
            "Your account has been deleted.\n"
            "Thank you for using ZIYRAK AI!"
        ),
        "lang_title": "Choose language:",
    },
}


def get_settings_keyboard(lang: str, notif_enabled: bool) -> InlineKeyboardMarkup:
    t = TEXTS.get(lang, TEXTS["uz"])
    notif_status = t["notifications_on"] if notif_enabled else t["notifications_off"]
    notif_icon = "🔔" if notif_enabled else "🔕"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{notif_icon} {notif_status}",
                callback_data="settings:toggle_notif"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🌐 " + t["change_lang"],
                callback_data="settings:change_lang"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🗑 " + t["delete_account"],
                callback_data="settings:delete"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🏠 " + t["back"],
                callback_data="menu:main"
            ),
        ],
    ])


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
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="menu:settings"),
        ],
    ])


def get_delete_keyboard(lang: str) -> InlineKeyboardMarkup:
    t = TEXTS.get(lang, TEXTS["uz"])
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ " + t["delete_confirm"],
                callback_data="settings:delete_confirm"
            ),
        ],
        [
            InlineKeyboardButton(
                text="❌ " + t["delete_cancel"],
                callback_data="menu:settings"
            ),
        ],
    ])


@router.message(Command("settings"))
async def cmd_settings(message: Message, db_user: User = None):
    await show_settings(message, db_user, is_callback=False)


@router.callback_query(F.data == "menu:settings")
async def settings_callback(callback: CallbackQuery, db_user: User = None):
    await show_settings(callback.message, db_user, is_callback=True)
    await callback.answer()


async def show_settings(message, db_user: User, is_callback: bool = False):
    lang = db_user.lang_code if db_user else "uz"
    t = TEXTS.get(lang, TEXTS["uz"])
    notif = getattr(db_user, "notifications_enabled", True)
    text = (
        t["title"] + "\n\n"
        f"ID: <code>{db_user.telegram_id}</code>\n"
        f"Tarif: {'Premium' if db_user.plan == 'pro' else 'Bepul'}\n"
    )
    keyboard = get_settings_keyboard(lang, notif)
    if is_callback:
        await message.answer(text, reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "settings:toggle_notif")
async def toggle_notifications(callback: CallbackQuery, db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    t = TEXTS.get(lang, TEXTS["uz"])

    async with async_session_maker() as session:
        from sqlalchemy import update
        from models.user import User as UserModel
        current = getattr(db_user, "notifications_enabled", True)
        new_value = not current
        await session.execute(
            update(UserModel)
            .where(UserModel.telegram_id == db_user.telegram_id)
            .values(notifications_enabled=new_value)
        )
        await session.commit()

    status_text = t["notif_enabled"] if new_value else t["notif_disabled"]
    await callback.answer(status_text, show_alert=True)

    keyboard = get_settings_keyboard(lang, new_value)
    notif = new_value
    text = (
        t["title"] + "\n\n"
        f"ID: <code>{db_user.telegram_id}</code>\n"
        f"Tarif: {'Premium' if db_user.plan == 'pro' else 'Bepul'}\n"
    )
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "settings:change_lang")
async def settings_change_lang(callback: CallbackQuery, db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    t = TEXTS.get(lang, TEXTS["uz"])
    await callback.message.answer(
        t["lang_title"],
        reply_markup=get_lang_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "settings:delete")
async def delete_account_warning(callback: CallbackQuery, db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    t = TEXTS.get(lang, TEXTS["uz"])
    await callback.message.answer(
        t["delete_warning"],
        reply_markup=get_delete_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "settings:delete_confirm")
async def delete_account_confirm(callback: CallbackQuery, db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    t = TEXTS.get(lang, TEXTS["uz"])

    async with async_session_maker() as session:
        from sqlalchemy import update
        from models.user import User as UserModel
        await session.execute(
            update(UserModel)
            .where(UserModel.telegram_id == db_user.telegram_id)
            .values(is_active=False, is_banned=True)
        )
        await session.commit()

    await callback.message.answer(t["deleted"])
    await callback.answer()
