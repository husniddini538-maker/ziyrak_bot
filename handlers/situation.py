from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from models.user import User
from ai.sie_engine import analyze_situation

router = Router()

class SituationStates(StatesGroup):
    waiting_for_text = State()

@router.callback_query(F.data == "menu:situation")
async def situation_menu(callback: CallbackQuery, state: FSMContext, db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    texts = {
        "uz": "🧠 <b>Vaziyat Yechimi</b>\n\nMuammongizni yozing 👇",
        "ru": "🧠 <b>Решение ситуации</b>\n\nОпишите проблему 👇",
        "en": "🧠 <b>Situation Solution</b>\n\nDescribe your problem 👇",
    }
    await callback.message.answer(texts.get(lang, texts["uz"]))
    await state.set_state(SituationStates.waiting_for_text)
    await callback.answer()

@router.message(SituationStates.waiting_for_text)
async def process_situation(message: Message, state: FSMContext, db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    wait_texts = {
        "uz": "🔄 Tahlil qilinmoqda...",
        "ru": "🔄 Анализируется...",
        "en": "🔄 Analyzing...",
    }
    wait_msg = await message.answer(wait_texts.get(lang, wait_texts["uz"]))
    result = await analyze_situation(message.text, lang)
    await wait_msg.delete()
    await message.answer(f"📋 <b>ZIYRAK AI:</b>\n\n{result}")
    await state.clear()
