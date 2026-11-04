import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import ADMIN_ID
from database import (
    create_attempt,
    save_attempt_answer,
    finish_attempt,
    get_user_attempt_number,
    get_current_time_str,
    update_user_activity
)
from services.quiz_service import QuizService
from keyboards import (
    get_main_keyboard,
    get_quiz_count_keyboard,
    get_quiz_options_keyboard,
    get_quiz_end_keyboard
)

logger = logging.getLogger(__name__)

router = Router(name="quiz_router")


class QuizStates(StatesGroup):
    waiting_for_count = State()
    in_quiz = State()


@router.message(F.text.in_(["🚀 Testni boshlash", "🔄 Qayta test ishlash"]))
async def ask_question_count(message: Message, state: FSMContext):
    """
    Foydalanuvchiga savollar sonini tanlashni taklif qiladi (5-bo'lim).
    """
    await state.clear()
    if message.from_user:
        await update_user_activity(message.from_user.id)

    total_avail = QuizService.get_total_questions_count()
    await state.set_state(QuizStates.waiting_for_count)

    text = (
        f"📚 Bizda jami {total_avail} ta test mavjud.\n\n"
        "Nechta test ishlamoqchisiz?"
    )
    await message.answer(text, reply_markup=get_quiz_count_keyboard())


@router.message(QuizStates.waiting_for_count)
async def process_question_count(message: Message, state: FSMContext):
    """
    Foydalanuvchi kiritgan sonni tekshiradi va testni boshlaydi (5-bo'lim validatsiyasi).
    """
    raw_text = message.text.strip() if message.text else ""

    if raw_text == "🏠 Bosh menyu":
        await state.clear()
        await message.answer("🏠 Asosiy menyudasiz:", reply_markup=get_main_keyboard())
        return

    # Validatsiya 1: Harf yoki noto'g'ri qiymat
    if not raw_text.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting.")
        return

    count = int(raw_text)
    total_avail = QuizService.get_total_questions_count()

    # Validatsiya 2: 0 yoki manfiy son
    if count <= 0:
        await message.answer(f"Iltimos, 1 dan {total_avail} gacha bo‘lgan sonni kiriting.")
        return

    # Validatsiya 3: 84 tadan ko'p son
    if count > total_avail:
        await message.answer(
            f"Uzr, bizda buncha test yo‘q. Bizda jami {total_avail} ta test mavjud. "
            f"Iltimos, {total_avail} yoki undan kam son kiriting."
        )
        return

    # Savollarni tasodifiy shakllantirish (6-bo'lim)
    try:
        questions = QuizService.generate_quiz(count)
    except Exception as e:
        logger.error("Savollarni shakllantirishda xatolik: %s", e)
        await message.answer("Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")
        return

    # Urinishni bazada yaratish
    attempt_id = await create_attempt(
        user_id=message.from_user.id,
        total_questions=count
    )

    # Holatni saqlash
    await state.set_state(QuizStates.in_quiz)
    await state.update_data(
        attempt_id=attempt_id,
        questions=questions,
        current_index=0,
        total_questions=count,
        correct_count=0,
        wrong_answers=[]
    )

    # 1-savolni yuborish (7-bo'lim)
    first_q = questions[0]
    q_text = QuizService.format_question_text(first_q, 1, count)
    await message.answer(
        q_text,
        reply_markup=get_quiz_options_keyboard(attempt_id, 0),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("ans:"))
async def process_quiz_answer(callback: CallbackQuery, state: FSMContext):
    """
    Foydalanuvchining savolga bergan javobini tekshiradi (8-bo'lim),
    natijani ko'rsatadi va keyingi savolni chiqaradi.
    """
    parts = callback.data.split(":")
    if len(parts) != 4:
        await callback.answer("Noto‘g‘ri ma'lumot!", show_alert=True)
        return

    _, attempt_id_str, q_idx_str, selected_letter = parts
    attempt_id = int(attempt_id_str)
    q_idx = int(q_idx_str)

    data = await state.get_data()
    stored_attempt_id = data.get("attempt_id")
    stored_current_idx = data.get("current_index")

    # Qayta bosish yoki eskirgan sessiyani himoyalash
    if stored_attempt_id != attempt_id or stored_current_idx is None:
        await callback.answer("⚠️ Ushbu test yakunlangan yoki boshqa sessiya faol.", show_alert=True)
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        return

    if stored_current_idx != q_idx:
        # Foydalanuvchi allaqachon javob berilgan savolni qayta bosgan
        await callback.answer("⚠️ Siz ushbu savolga allaqachon javob bergansiz!", show_alert=False)
        return

    # Javobni tekshirish
    questions = data["questions"]
    current_q = questions[q_idx]
    correct_letter = current_q["correct_letter"]
    correct_text = current_q["correct_text"]
    selected_text = current_q["options"].get(selected_letter, "")

    is_correct = (selected_letter == correct_letter)
    correct_count = data.get("correct_count", 0) + (1 if is_correct else 0)
    wrong_answers = list(data.get("wrong_answers", []))

    if not is_correct:
        wrong_answers.append({
            "question": current_q["question"],
            "selected": f"{selected_letter}) {selected_text}",
            "correct": f"{correct_letter}) {correct_text}"
        })

    # Bazaga javobni yozish
    await save_attempt_answer(
        attempt_id=attempt_id,
        question_id=current_q["id"],
        selected_answer=f"{selected_letter}) {selected_text}",
        correct_answer=f"{correct_letter}) {correct_text}",
        is_correct=is_correct
    )

    next_idx = q_idx + 1
    total_questions = data["total_questions"]

    # FSM ma'lumotlarini yangilash
    await state.update_data(
        current_index=next_idx,
        correct_count=correct_count,
        wrong_answers=wrong_answers
    )

    # 8-bo'lim: Har bir javobdan keyin darhol natija ko'rsatish va tugmalarni o'chirish
    if is_correct:
        feedback_str = "✅ <b>To‘g‘ri javob!</b>"
    else:
        feedback_str = f"❌ <b>Noto‘g‘ri javob!</b>\n\nTo‘g‘ri javob: <b>{correct_text}</b>"

    # Eski savol matnini yangilash (foydalanuvchi qayta bosa olmasligi uchun)
    base_text = callback.message.html_text or callback.message.text or ""
    edited_text = (
        f"{base_text}\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"Sizning tanlovingiz: <b>{selected_letter}) {selected_text}</b>\n"
        f"{feedback_str}"
    )

    try:
        await callback.message.edit_text(
            edited_text,
            reply_markup=None,
            parse_mode="HTML"
        )
    except Exception:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass

    await callback.answer(
        text="✅ To‘g‘ri javob!" if is_correct else "❌ Noto‘g‘ri javob!",
        show_alert=False
    )

    # Agar savollar tugamagan bo'lsa, keyingi savolni chiqarish
    if next_idx < total_questions:
        next_q = questions[next_idx]
        next_q_text = QuizService.format_question_text(next_q, next_idx + 1, total_questions)
        await callback.message.answer(
            next_q_text,
            reply_markup=get_quiz_options_keyboard(attempt_id, next_idx),
            parse_mode="HTML"
        )
    else:
        # 9-bo'lim: Test yakunlandi!
        await state.clear()
        wrong_count = total_questions - correct_count
        percentage = (correct_count / total_questions) * 100.0
        finished_at = get_current_time_str()

        # Urinishni yakunlash
        await finish_attempt(attempt_id, correct_count, wrong_count, percentage)

        # Natija xabarini yuborish
        user_name = callback.from_user.full_name or "Foydalanuvchi"
        result_msg = QuizService.format_quiz_result(
            participant_name=user_name,
            total=total_questions,
            correct=correct_count,
            wrong=wrong_count,
            percentage=percentage
        )

        await callback.message.answer(
            result_msg,
            reply_markup=get_quiz_end_keyboard(),
            parse_mode="HTML"
        )

        # Xato savollar tahlilini yuborish
        if wrong_answers:
            wrong_chunks = QuizService.format_wrong_answers_blocks(wrong_answers)
            for chunk in wrong_chunks:
                await callback.message.answer(chunk, parse_mode="HTML")

        # 14-bo'lim: Administratorga xabarnoma yuborish
        try:
            attempt_num = await get_user_attempt_number(callback.from_user.id, attempt_id)
            admin_msg = QuizService.format_admin_notification(
                name=user_name,
                username=callback.from_user.username,
                telegram_id=callback.from_user.id,
                total=total_questions,
                correct=correct_count,
                wrong=wrong_count,
                percentage=percentage,
                attempt_number=attempt_num,
                finished_at=finished_at
            )
            await callback.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_msg,
                parse_mode="HTML"
            )
        except Exception as ex:
            logger.warning("Admin xabarnomasini yuborishda xatolik yuz berdi: %s", ex)

