from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from models.user import User
from ai.doc_gen_ai import generate_document

router = Router()


class DocStates(StatesGroup):
    choosing_type = State()
    waiting_for_info = State()


DOC_TYPES = {
    "uz": {
        "ariza": "📝 Ariza",
        "shikoyat": "⚠️ Shikoyat",
        "shartnoma": "📋 Shartnoma",
        "rezyume": "👤 Rezyume/CV",
    },
    "ru": {
        "ariza": "📝 Заявление",
        "shikoyat": "⚠️ Жалоба",
        "shartnoma": "📋 Договор",
        "rezyume": "👤 Резюме/CV",
    },
    "en": {
        "ariza": "📝 Application",
        "shikoyat": "⚠️ Complaint",
        "shartnoma": "📋 Contract",
        "rezyume": "👤 Resume/CV",
    },
}

TEXTS = {
    "uz": {
        "choose": "📄 Qanday hujjat kerak?",
        "info": "Ma'lumot yozing:\n\nMasalan:\n{example}",
        "generating": "📝 Hujjat tayyorlanmoqda...",
        "done": "✅ Hujjatingiz tayyor!\n\n",
        "new_doc": "🔄 Yangi hujjat",
        "main_menu": "🏠 Asosiy menyu",
        "examples": {
            "ariza": "Ish joyim, lavozimim, nimani so'remoqchiman",
            "shikoyat": "Kim haqida, qanday muammo, qachon bo'ldi",
            "shartnoma": "Tomonlar, shartnoma predmeti, to'lov miqdori",
            "rezyume": "Ismim, yoshim, tajribam, ta'limim, ko'nikmalarim",
        }
    },
    "ru": {
        "choose": "📄 Какой документ нужен?",
        "info": "Напишите информацию:\n\nНапример:\n{example}",
        "generating": "📝 Документ готовится...",
        "done": "✅ Ваш документ готов!\n\n",
        "new_doc": "🔄 Новый документ",
        "main_menu": "🏠 Главное меню",
        "examples": {
            "ariza": "Место работы, должность, что прошу",
            "shikoyat": "На кого жалоба, проблема, когда произошло",
            "shartnoma": "Стороны, предмет договора, сумма",
            "rezyume": "Имя, возраст, опыт, образование, навыки",
        }
    },
    "en": {
        "choose": "📄 What document do you need?",
        "info": "Write your information:\n\nExample:\n{example}",
        "generating": "📝 Generating document...",
        "done": "✅ Your document is ready!\n\n",
        "new_doc": "🔄 New document",
        "main_menu": "🏠 Main menu",
        "examples": {
            "ariza": "Workplace, position, what I'm requesting",
            "shikoyat": "Who to complain about, problem, when it happened",
            "shartnoma": "Parties, subject, payment amount",
            "rezyume": "Name, age, experience, education, skills",
        }
    },
}


def get_doc_type_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    types = DOC_TYPES.get(lang, DOC_TYPES["uz"])
    buttons = []
    items = list(types.items())
    for i in range(0, len(items), 2):
        row = []
        for key, label in items[i:i+2]:
            row.append(InlineKeyboardButton(
                text=label,
                callback_data=f"doctype:{key}"
            ))
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_after_doc_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    t = TEXTS.get(lang, TEXTS["uz"])
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t["new_doc"], callback_data="menu:document"),
            InlineKeyboardButton(text=t["main_menu"], callback_data="menu:main"),
        ]
    ])


@router.callback_query(F.data == "menu:document")
async def document_menu(callback: CallbackQuery, state: FSMContext,
                         db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    t = TEXTS.get(lang, TEXTS["uz"])
    await callback.message.answer(
        t["choose"],
        reply_markup=get_doc_type_keyboard(lang)
    )
    await state.set_state(DocStates.choosing_type)
    await callback.answer()


@router.callback_query(F.data.startswith("doctype:"), DocStates.choosing_type)
async def doc_type_chosen(callback: CallbackQuery, state: FSMContext,
                           db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    doc_type = callback.data.split(":")[1]
    t = TEXTS.get(lang, TEXTS["uz"])
    example = t["examples"].get(doc_type, "")
    await state.update_data(doc_type=doc_type)
    await callback.message.answer(
        t["info"].format(example=example)
    )
    await state.set_state(DocStates.waiting_for_info)
    await callback.answer()


@router.message(DocStates.waiting_for_info)
async def process_document(message: Message, state: FSMContext,
                             db_user: User = None):
    lang = db_user.lang_code if db_user else "uz"
    t = TEXTS.get(lang, TEXTS["uz"])
    data = await state.get_data()
    doc_type = data.get("doc_type", "ariza")

    wait_msg = await message.answer(t["generating"])

    result = await generate_document(doc_type, message.text, lang)

    await wait_msg.delete()

    # Matn sifatida yuborish
    await message.answer(
        t["done"] + result,
        reply_markup=get_after_doc_keyboard(lang)
    )

    # TXT fayl sifatida ham yuborish
    file_content = result.encode("utf-8")
    doc_names = {
        "ariza": "ariza", "shikoyat": "shikoyat",
        "shartnoma": "shartnoma", "rezyume": "rezyume"
    }
    filename = f"{doc_names.get(doc_type, 'hujjat')}.txt"
    await message.answer_document(
        BufferedInputFile(file_content, filename=filename),
        caption="📎 Hujjat fayl sifatida"
    )

    await state.clear()
