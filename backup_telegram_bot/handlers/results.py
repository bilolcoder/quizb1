import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from database import get_user_stats, get_top_users, update_user_activity

logger = logging.getLogger(__name__)

router = Router(name="results_router")


@router.message(F.text == "📊 Mening natijalarim")
@router.message(Command("myresults"))
async def handle_my_results(message: Message):
    """
    11-bo'lim: Foydalanuvchining shaxsiy statistikasini chiqaradi:
    - Jami test ishlagan soni
    - Eng yaxshi natijasi
    - Oxirgi natijasi
    - O‘rtacha foizi
    - To‘g‘ri javoblar soni
    - Noto‘g‘ri javoblar soni
    """
    user = message.from_user
    if not user:
        return

    await update_user_activity(user.id)
    stats = await get_user_stats(user.id)

    if stats.get("total_tests", 0) == 0:
        await message.answer(
            "📊 <b>Siz hali birorta ham test ishlamagansiz.</b>\n\n"
            "Testni boshlash uchun «🚀 Testni boshlash» tugmasini bosing!",
            parse_mode="HTML"
        )
        return

    best = stats.get("best_attempt")
    latest = stats.get("latest_attempt")

    best_str = (
        f"{best['correct_answers']} / {best['total_questions']} "
        f"({int(best['percentage']) if best['percentage'].is_integer() else best['percentage']}%)"
        if best else "Mavjud emas"
    )

    latest_str = (
        f"{latest['correct_answers']} / {latest['total_questions']} "
        f"({int(latest['percentage']) if latest['percentage'].is_integer() else latest['percentage']}%)"
        if latest else "Mavjud emas"
    )

    user_name = user.full_name or "Foydalanuvchi"

    text = (
        f"📊 <b>SIZNING SHAXSIY NATIJALARINGIZ</b>\n\n"
        f"👤 <b>Foydalanuvchi:</b> {user_name}\n"
        f"🔢 <b>Jami test ishlagan soningiz:</b> {stats['total_tests']} ta\n"
        f"🌟 <b>Eng yaxshi natijangiz:</b> {best_str}\n"
        f"⏱ <b>Oxirgi natijangiz:</b> {latest_str}\n"
        f"📈 <b>O‘rtacha foizingiz:</b> {stats['avg_percentage']}%\n"
        f"✅ <b>Jami to‘g‘ri javoblaringiz:</b> {stats['total_correct']} ta\n"
        f"❌ <b>Jami noto‘g‘ri javoblaringiz:</b> {stats['total_wrong']} ta"
    )

    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "🏆 Reyting")
@router.message(Command("leaderboard"))
async def handle_rating(message: Message):
    """
    12-bo'lim: Eng yaxshi 10 ta foydalanuvchi reytingi.
    Reyting eng yaxshi natija foizi va to'g'ri javoblar soni bo'yicha tartiblanadi.
    """
    if message.from_user:
        await update_user_activity(message.from_user.id)

    top_users = await get_top_users(limit=10)

    if not top_users:
        await message.answer(
            "🏆 <b>Hozircha reyting mavjud emas.</b>\n\n"
            "Birinchi bo‘lib test topshiring va peshqadamga aylaning!",
            parse_mode="HTML"
        )
        return

    medals = ["🥇", "🥈", "🥉"]
    lines = ["🏆 <b>ENG YAXSHI NATIJALAR (TOP-10)</b>\n"]

    for idx, item in enumerate(top_users, 1):
        medal = medals[idx - 1] if idx <= 3 else f"{idx}."
        first_name = item.get("first_name") or "Ishtirokchi"
        pct = item.get("percentage", 0.0)
        pct_formatted = int(pct) if float(pct).is_integer() else round(pct, 1)
        correct = item.get("correct_answers", 0)
        total = item.get("total_questions", 0)

        lines.append(f"{medal} <b>{first_name}</b> — {pct_formatted}% ({correct}/{total})")

    lines.append("\n💡 <i>Reyting eng yuqori foiz va to‘g‘ri javoblar soni asosida tuziladi.</i>")

    await message.answer("\n".join(lines), parse_mode="HTML")

