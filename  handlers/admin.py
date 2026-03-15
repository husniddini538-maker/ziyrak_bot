from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.connection import async_session_maker
from config.settings import settings

router = Router()


class AdminStates(StatesGroup):
    waiting_broadcast = State()


def is_admin(telegram_id: int) -> bool:
    return telegram_id in settings.admin_ids_list


def get_admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats"),
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin:users"),
        ],
        [
            InlineKeyboardButton(text="📢 Broadcast", callback_data="admin:broadcast"),
            InlineKeyboardButton(text="🔗 Referrallar", callback_data="admin:referrals"),
        ],
        [
            InlineKeyboardButton(text="💎 Premiumlar", callback_data="admin:premiums"),
            InlineKeyboardButton(text="🔄 Yangilash", callback_data="admin:refresh"),
        ],
    ])


async def get_stats() -> dict:
    from sqlalchemy import select, func
    from models.user import User
    from models.referral import Referral
    from datetime import datetime, timedelta

    async with async_session_maker() as session:
        total = await session.execute(select(func.count()).select_from(User))
        total_users = total.scalar() or 0

        today = datetime.now().date()
        new_today = await session.execute(
            select(func.count()).select_from(User).where(
                func.date(User.created_at) == today
            )
        )
        new_today_count = new_today.scalar() or 0

        week_ago = datetime.now() - timedelta(days=7)
        new_week = await session.execute(
            select(func.count()).select_from(User).where(
                User.created_at >= week_ago
            )
        )
        new_week_count = new_week.scalar() or 0

        premiums = await session.execute(
            select(func.count()).select_from(User).where(User.plan == "pro")
        )
        premium_count = premiums.scalar() or 0

        total_refs = await session.execute(
            select(func.count()).select_from(Referral)
        )
        ref_count = total_refs.scalar() or 0

        active = await session.execute(
            select(func.count()).select_from(User).where(
                User.daily_requests_used > 0
            )
        )
        active_count = active.scalar() or 0

    return {
        "total": total_users,
        "new_today": new_today_count,
        "new_week": new_week_count,
        "premium": premium_count,
        "referrals": ref_count,
        "active": active_count,
    }


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Ruxsat yo'q!")
        return

    stats = await get_stats()
    text = (
        "<b>👨‍💼 Admin Panel</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total']}</b>\n"
        f"🆕 Bugun yangi: <b>{stats['new_today']}</b>\n"
        f"📅 Haftalik yangi: <b>{stats['new_week']}</b>\n"
        f"💎 Premium: <b>{stats['premium']}</b>\n"
        f"🔗 Referrallar: <b>{stats['referrals']}</b>\n"
        f"⚡ Faol bugun: <b>{stats['active']}</b>\n"
    )
    await message.answer(text, reply_markup=get_admin_keyboard())


@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return

    stats = await get_stats()
    conv = round(stats['premium'] / stats['total'] * 100, 1) if stats['total'] > 0 else 0
    ref_percent = round(stats['referrals'] / stats['total'] * 100, 1) if stats['total'] > 0 else 0

    text = (
        "<b>📊 Batafsil Statistika</b>\n\n"
        f"👥 Jami: <b>{stats['total']}</b>\n"
        f"🆕 Bugun: <b>{stats['new_today']}</b>\n"
        f"📅 Hafta: <b>{stats['new_week']}</b>\n"
        f"💎 Premium: <b>{stats['premium']}</b>\n"
        f"🔗 Referrallar: <b>{stats['referrals']}</b>\n"
        f"⚡ Faol: <b>{stats['active']}</b>\n\n"
        f"💰 Konversiya: <b>{conv}%</b>\n"
        f"🔗 Referral: <b>{ref_percent}%</b>\n"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin:users")
async def admin_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return

    from sqlalchemy import select
    from models.user import User

    async with async_session_maker() as session:
        result = await session.execute(
            select(User).order_by(User.created_at.desc()).limit(10)
        )
        users = result.scalars().all()

    text = "<b>👥 Oxirgi 10 foydalanuvchi:</b>\n\n"
    for i, user in enumerate(users, 1):
        username = f"@{user.username}" if user.username else "—"
        plan = "💎" if user.plan == "pro" else "🆓"
        created = user.created_at.strftime("%d.%m %H:%M") if user.created_at else "—"
        text += (
            f"{i}. {plan} <b>{user.full_name or 'Nomsiz'}</b>\n"
            f"   {username} | {user.lang_code.upper()} | {created}\n"
        )

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin:back")]
        ])
    )
    await callback.answer()


@router.callback_query(F.data == "admin:referrals")
async def admin_referrals(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return

    from sqlalchemy import select, func
    from models.referral import Referral

    async with async_session_maker() as session:
        top_referrers = await session.execute(
            select(
                Referral.referrer_telegram_id,
                func.count(Referral.id).label("count")
            )
            .group_by(Referral.referrer_telegram_id)
            .order_by(func.count(Referral.id).desc())
            .limit(10)
        )
        top = top_referrers.all()

    text = "<b>🔗 Top 10 Referrallar:</b>\n\n"
    for i, (tg_id, count) in enumerate(top, 1):
        text += f"{i}. ID: <code>{tg_id}</code> — {count} ta\n"

    if not top:
        text += "Hali referrallar yo'q"

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin:back")]
        ])
    )
    await callback.answer()


@router.callback_query(F.data == "admin:premiums")
async def admin_premiums(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return

    from sqlalchemy import select
    from models.user import User

    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.plan == "pro")
        )
        premiums = result.scalars().all()

    text = f"<b>💎 Premium foydalanuvchilar: {len(premiums)}</b>\n\n"
    for i, user in enumerate(premiums, 1):
        username = f"@{user.username}" if user.username else "—"
        text += f"{i}. <b>{user.full_name or 'Nomsiz'}</b> {username}\n"

    if not premiums:
        text += "Hali premium foydalanuvchilar yo'q"

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin:back")]
        ])
    )
    await callback.answer()


@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return

    await callback.message.answer(
        "<b>📢 Broadcast Xabar</b>\n\n"
        "Barcha foydalanuvchilarga yubormoqchi bo'lgan xabarni yozing:\n\n"
        "<i>HTML format ishlaydi: bold, italic, code</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin:cancel")]
        ])
    )
    await state.set_state(AdminStates.waiting_broadcast)
    await callback.answer()


@router.message(AdminStates.waiting_broadcast)
async def admin_broadcast_send(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    from sqlalchemy import select
    from models.user import User

    sent = 0
    failed = 0

    wait_msg = await message.answer("📤 Yuborilmoqda...")

    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.is_active == True)
        )
        users = result.scalars().all()

    for user in users:
        try:
            await message.bot.send_message(
                chat_id=user.telegram_id,
                text=f"📢 <b>ZIYRAK AI:</b>\n\n{message.text}",
                parse_mode="HTML"
            )
            sent += 1
        except Exception:
            failed += 1

    await wait_msg.delete()
    await message.answer(
        f"✅ Broadcast tugadi!\n\n"
        f"📤 Yuborildi: <b>{sent}</b>\n"
        f"❌ Xato: <b>{failed}</b>",
        reply_markup=get_admin_keyboard()
    )
    await state.clear()


@router.callback_query(F.data == "admin:cancel")
async def admin_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "<b>👨‍💼 Admin Panel</b>",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer("Bekor qilindi")


@router.callback_query(F.data == "admin:refresh")
async def admin_refresh(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return

    stats = await get_stats()
    text = (
        "<b>👨‍💼 Admin Panel</b>\n\n"
        f"👥 Jami: <b>{stats['total']}</b>\n"
        f"🆕 Bugun: <b>{stats['new_today']}</b>\n"
        f"📅 Hafta: <b>{stats['new_week']}</b>\n"
        f"💎 Premium: <b>{stats['premium']}</b>\n"
        f"🔗 Referrallar: <b>{stats['referrals']}</b>\n"
        f"⚡ Faol: <b>{stats['active']}</b>\n"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard())
    await callback.answer("✅ Yangilandi!")


@router.callback_query(F.data == "admin:back")
async def admin_back(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!")
        return

    stats = await get_stats()
    text = (
        "<b>👨‍💼 Admin Panel</b>\n\n"
        f"👥 Jami: <b>{stats['total']}</b>\n"
        f"🆕 Bugun: <b>{stats['new_today']}</b>\n"
        f"💎 Premium: <b>{stats['premium']}</b>\n"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard())
    await callback.answer()