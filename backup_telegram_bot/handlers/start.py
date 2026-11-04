import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import register_or_update_user
from keyboards import get_main_keyboard

logger = logging.getLogger(__name__)

router = Router(name="start_router")


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext):
    """
    /start buyrug'i:
    - Foydalanuvchini bazaga ro'yxatdan o'tkazadi
    - 4-bo'limdagi xabarni va asosiy menyuni chiqaradi
    """
    await state.clear()

    user = message.from_user
    if user:
        await register_or_update_user(
            telegram_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username
        )

    text = (
        "Assalomu alaykum!\n\n"
        "Iqtisodiy tahlil fanidan yakuniy test botiga xush kelibsiz!\n\n"
        "Bizda jami 84 ta test savoli mavjud.\n\n"
        "Testni boshlash uchun quyidagi tugmani bosing."
    )

    await message.answer(text, reply_markup=get_main_keyboard())


@router.message(F.text == "🏠 Bosh menyu")
@router.message(Command("menu"))
async def handle_main_menu(message: Message, state: FSMContext):
    """Foydalanuvchini asosiy menyuga qaytaradi."""
    await state.clear()
    await message.answer(
        "🏠 Asosiy menyudasiz. Kerakli bo‘limni tanlang:",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "ℹ️ Bot haqida")
async def handle_about(message: Message):
    """Bot haqida ma'lumot beruvchi xabar."""
    text = (
        "ℹ️ <b>BOT HAQIDA MA'LUMOT</b>\n\n"
        "📚 <b>Fan:</b> Iqtisodiy tahlil\n"
        "❓ <b>Jami savollar bazasi:</b> 84 ta rasmiy test savoli\n\n"
        "🎯 <b>Afzalliklari:</b>\n"
        "• Savollar sonini o‘zingiz tanlaysiz (1 dan 84 gacha)\n"
        "• Savollar va javob variantlari har safar tasodifiy aralashtiriladi\n"
        "• Har bir javobdan so‘ng to‘g‘ri javob darhol ko‘rsatiladi\n"
        "• Test yakunida xato qilingan savollar tahlili taqdim etiladi\n"
        "• Urinishlar soni cheksiz va barcha natijalar saqlanadi\n"
        "• Foydalanuvchilar o‘rtasida umumiy reyting yuritiladi\n\n"
        "Bilimingizni sinash uchun «🚀 Testni boshlash» tugmasini bosing!"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_keyboard())

