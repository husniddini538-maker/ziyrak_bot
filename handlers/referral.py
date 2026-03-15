from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from models.user import User
from database.connection import async_session_maker
from database.repositories.user_repo import UserRepository
from database.repositories.referral_repo import ReferralRepository

router = Router()

TEXTS = {
    "uz": {
        "title": "👥 Referral Tizimi",
        "your_link": "Sizning referral havolangiz",
        "count": "Taklif qilganlar soni",
        "reward_info": (
            "Mukofotlar:\n"
            "• 3 do'st = 1 oy Premium bepul\n"
            "• 10 do'st = Pro tarif 50% chegirma\n"
            "• 20 do'st = Pro tarif umrboqiy bepul"
        ),
        "how_to": (
            "Qanday ishlaydi:\n"
            "1. Havolangizni do'stingizga yuboring\n"
            "2. Do'stingiz botga kiradi\n"
            "3. Siz mukofot olasiz!"
        ),
        "share_text": (
            "Do'stim, ZIYRAK AI botini sinab ko'r!\n"
            "Har qanday huquqiy, biznes va moliyaviy savollaringizga\n"
            "AI yordamida javob olasiz.\n\n"
            "Bot: @Ziyrakn1_bot\n"
            "Kirish havolasi: {link}"
        ),
        "share_btn": "📤 Do'stlarga ulashish",
        "back": "🏠 Asosiy menyu",
        "progress": "Maqsadga progress",
        "next_reward": "Keyingi mukofot",
        "people": "kishi",
        "needed": "kishi kerak",
        "welcome_ref": (
            "Salom! Siz do'stingiz taklifi orqali keldingiz.\n"
            "ZIYRAK AI ga xush kelibsiz! 🎉"
        ),
    },
    "ru": {
        "title": "👥 Реферальная система",
        "your_link": "Ваша реферальная ссылка",
        "count": "Приглашено друзей",
        "reward_info": (
            "Награды:\n"
            "• 3 друга = 1 месяц Premium бесплатно\n"
            "• 10 друзей = Pro тариф 50% скидка\n"
            "• 20 друзей = Pro тариф навсегда бесплатно"
        ),
        "how_to": (
            "Как работает:\n"
            "1. Отправьте ссылку другу\n"
            "2. Друг заходит в бот\n"
            "3. Вы получаете награду!"
        ),
        "share_text": (
            "Попробуй ZIYRAK AI бот!\n"
            "Получай ответы на юридические, бизнес\n"
            "и финансовые вопросы с помощью AI.\n\n"
            "Бот: @Ziyrakn1_bot\n"
            "Ссылка: {link}"
        ),
        "share_btn": "📤 Поделиться с друзьями",
        "back": "🏠 Главное меню",
        "progress": "Прогресс к цели",
        "next_reward": "Следующая награда",
        "people": "чел.",
        "needed": "чел. нужно",
        "welcome_ref": (
            "Привет! Вы пришли по приглашению друга.\n"
            "Добро пожаловать в ZIYRAK AI! 🎉"
        ),
    },
    "en": {
        "title": "👥 Referral System",
        "your_link": "Your referral link",
        "count": "Friends invited",
        "reward_info": (
            "Rewards:\n"
            "• 3 friends = 1 month Premium free\n"
            "• 10 friends = Pro plan 50% discount\n"
            "• 20 friends = Pro plan forever free"
        ),
        "how_to": (
            "How it works:\n"
            "1. Send your link to a friend\n"
            "2. Friend joins the bot\n"
            "3. You get a reward!"
        ),
        "share_text": (
            "Try ZIYRAK AI bot!\n"
            "Get answers to legal, business\n"
            "and financial questions with AI.\n\n"
            "Bot: @Ziyrakn1_bot\n"
            "Link: {link}"
        ),
        "share_btn": "📤 Share with friends",
        "back": "🏠 Main menu",
        "progress": "Progress to goal",
        "next_reward": "Next reward",
        "people": "people",
        "needed": "people needed",
        "welcome_ref": (
            "Hello! You came through a friend's invitation.\n"
            "Welcome to ZIYRAK AI! 🎉"
        ),
    },
}

REWARDS = [3, 10, 20]


def get_referral_keyboard(lang: str, share_text: str) -> InlineKeyboardMarkup:
    t = TEXTS.get(lang, TEXTS["uz"])
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=t["share_btn"],
                switch_inline_query=share_text
            ),
        ],
        [
            InlineKeyboardButton(
                text=t["back"],
                callback_data="menu:main"
            ),
        ],
    ])


def build_progress_bar(current: int, target: int) -> str:
    if target == 0:
        return ""
    percent = min(int((current / target) * 10), 10)
    bar = "█" * percent + "░" * (10 - percent)
    return f"[{bar}] {current}/{target}"


def get_next_reward(count: int) -> int | None:
    for r in REWARDS:
        if count < r:
            return r
    return None


@router.message(Command("referral"))
async def cmd_referral(message: Message, db_user: User = None):
    await show_referral(message, db_user, is_callback=False)


@router.callback_query(F.data == "menu:referral")
async def referral_callback(callback: CallbackQuery, db_user: User = None):
    await show_referral(callback.message, db_user, is_callback=True)
    await callback.answer()


async def show_referral(message, db_user: User, is_callback: bool = False):
    lang = db_user.lang_code if db_user else "uz"
    t = TEXTS.get(lang, TEXTS["uz"])

    async with async_session_maker() as session:
        ref_repo = ReferralRepository(session)
        count = await ref_repo.count_referrals(db_user.telegram_id)

    bot_username = "Ziyrakn1_bot"
    ref_link = f"https://t.me/{bot_username}?start=ref{db_user.telegram_id}"

    next_reward = get_next_reward(count)
    progress = build_progress_bar(count, next_reward) if next_reward else "🏆 MAX"

    text = (
        f"<b>{t['title']}</b>\n\n"
        f"🔗 <b>{t['your_link']}:</b>\n"
        f"<code>{ref_link}</code>\n\n"
        f"👥 <b>{t['count']}:</b> {count} {t['people']}\n\n"
        f"📊 <b>{t['progress']}:</b>\n"
        f"{progress}\n\n"
        f"🎁 <b>{t['reward_info']}</b>\n\n"
        f"❓ <b>{t['how_to']}</b>"
    )

    share_text = t["share_text"].format(link=ref_link)

    if is_callback:
        await message.answer(
            text,
            reply_markup=get_referral_keyboard(lang, share_text)
        )
    else:
        await message.answer(
            text,
            reply_markup=get_referral_keyboard(lang, share_text)
        )
