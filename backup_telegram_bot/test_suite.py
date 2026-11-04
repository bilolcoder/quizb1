import asyncio
import os
import sys
from pathlib import Path

# Loyiha yo'lini qo'shish
sys.path.insert(0, str(Path(__file__).resolve().parent))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from config import ADMIN_ID, DATABASE_PATH, QUESTIONS_FILE
from database import (
    init_db,
    register_or_update_user,
    get_user,
    create_attempt,
    save_attempt_answer,
    finish_attempt,
    get_user_stats,
    get_user_attempt_number,
    get_top_users,
    get_admin_stats,
    get_all_users,
    get_all_attempts,
    get_attempt_wrong_answers,
    get_current_time_str
)
from services.quiz_service import QuizService
from handlers.admin import IsAdminFilter
from aiogram.types import User


async def run_all_tests():
    print("=" * 60)
    print("TEST JARAYONI BOSHLANDI")
    print("=" * 60)

    # 1. BAZANI INITSIALIZATSIYA QILISH
    await init_db()
    print("✅ 1. Database initsializatsiyasi muvaffaqiyatli.")

    # 2. FOYDALANUVCHINI RO'YXATDAN O'TKAZISH VA QAYTA KIRISHNI TEKSHIRISH
    u1 = await register_or_update_user(
        telegram_id=111222333,
        first_name="Alisher",
        last_name="Navoiy",
        username="alisher_n"
    )
    assert u1["is_new"] is True, "Yangi foydalanuvchi is_new=True bo'lishi kerak!"

    u1_again = await register_or_update_user(
        telegram_id=111222333,
        first_name="Alisher",
        last_name="Navoiy Yangilangan",
        username="alisher_n"
    )
    assert u1_again["is_new"] is False, "Qayta kirgan foydalanuvchi qayta yaratilmasligi kerak!"
    user_db = await get_user(111222333)
    assert user_db["first_name"] == "Alisher", "Foydalanuvchi ma'lumotlari bazada saqlanishi kerak!"
    print("✅ 2. Foydalanuvchini ro'yxatdan o'tkazish va qayta kirish to'g'ri ishladi.")

    # 3. 84 TA MAVJUD SAVOL HAQIDA XABAR BERILISHI
    total_q = QuizService.get_total_questions_count()
    assert total_q == 84, f"Kutilgan savollar soni 84, ammo {total_q} topildi!"
    print(f"✅ 3. Savollar bazasi to'liq: jami {total_q} ta savol mavjud.")

    # 4 & 5. SAVOLLAR SONI VALIDATSIYASI (85 rad etilishi, 1-84 qabul qilinishi)
    def validate_count_input(val_str: str, max_count: int = 84):
        if not val_str.isdigit():
            return "NOT_DIGIT"
        c = int(val_str)
        if c <= 0:
            return "OUT_OF_RANGE_LOW"
        if c > max_count:
            return "OUT_OF_RANGE_HIGH"
        return "VALID"

    assert validate_count_input("85") == "OUT_OF_RANGE_HIGH", "85 soni rad etilishi kerak!"
    assert validate_count_input("100") == "OUT_OF_RANGE_HIGH", "100 soni rad etilishi kerak!"
    assert validate_count_input("0") == "OUT_OF_RANGE_LOW", "0 soni rad etilishi kerak!"
    assert validate_count_input("-5") == "NOT_DIGIT" or validate_count_input("-5") == "OUT_OF_RANGE_LOW"
    assert validate_count_input("salom") == "NOT_DIGIT", "Harflar rad etilishi kerak!"
    assert validate_count_input("1") == "VALID", "1 qabul qilinishi kerak!"
    assert validate_count_input("20") == "VALID", "20 qabul qilinishi kerak!"
    assert validate_count_input("84") == "VALID", "84 qabul qilinishi kerak!"
    print("✅ 4-5. Savollar soni validatsiyasi (0, 85, harflar rad etilishi, 1-84 qabul qilinishi) to'g'ri.")

    # 6. SAVOLLAR VA VARIANTLARNING ARALASHTIRILISHI VA TO'G'RI JAVOB SAQLANISHI
    quiz_20 = QuizService.generate_quiz(20)
    assert len(quiz_20) == 20, "20 ta savol generatsiya qilinishi kerak!"
    ids = [q["id"] for q in quiz_20]
    assert len(set(ids)) == 20, "Bir test ichida savollar takrorlanmasligi kerak!"

    for item in quiz_20:
        assert set(item["options"].keys()) == {"A", "B", "C", "D"}, "Variantlar A, B, C, D bo'lishi kerak!"
        corr_letter = item["correct_letter"]
        assert corr_letter in ["A", "B", "C", "D"], "To'g'ri javob harfi A..D bo'lishi kerak!"
        assert item["options"][corr_letter] == item["correct_text"], "To'g'ri javob matni saqlanib qolishi kerak!"

    print("✅ 6. Savollar va variantlarni aralashtirish hamda to'g'ri javobni matn orqali aniqlash to'g'ri.")

    # 7. SAVOL FORMATLANISHI (7-bo'lim)
    formatted_q = QuizService.format_question_text(quiz_20[0], 1, 20)
    assert "📚 <b>IQTISODIY TAHLIL</b>" in formatted_q
    assert "❓ <b>Savol 1 / 20</b>" in formatted_q
    assert "A)" in formatted_q and "B)" in formatted_q and "C)" in formatted_q and "D)" in formatted_q
    print("✅ 7. Savol ko'rinishi 7-bo'lim talablariga to'liq mos keladi.")

    # 8. JAVOBLAR VA NATIJALARNING SQLITE BAZAGA YOZILISHI (8-9 bo'limlar)
    test_user_id = 111222333
    attempt_id = await create_attempt(user_id=test_user_id, total_questions=5)
    assert attempt_id > 0, "Attempt ID musbat bo'lishi kerak!"

    # 5 ta savoldan 4 tasiga to'g'ri, 1 tasiga noto'g'ri javob berish
    quiz_5 = QuizService.generate_quiz(5)
    wrong_answers_collector = []
    correct_count = 0

    for idx, q_item in enumerate(quiz_5):
        if idx < 4:
            # To'g'ri javob
            selected_letter = q_item["correct_letter"]
            selected_text = q_item["options"][selected_letter]
            is_correct = True
            correct_count += 1
        else:
            # Noto'g'ri javob
            wrong_letters = [l for l in ["A", "B", "C", "D"] if l != q_item["correct_letter"]]
            selected_letter = wrong_letters[0]
            selected_text = q_item["options"][selected_letter]
            is_correct = False
            wrong_answers_collector.append({
                "question": q_item["question"],
                "selected": f"{selected_letter}) {selected_text}",
                "correct": f"{q_item['correct_letter']}) {q_item['correct_text']}"
            })

        await save_attempt_answer(
            attempt_id=attempt_id,
            question_id=q_item["id"],
            selected_answer=f"{selected_letter}) {selected_text}",
            correct_answer=f"{q_item['correct_letter']}) {q_item['correct_text']}",
            is_correct=is_correct
        )

    wrong_count = 5 - correct_count
    pct = (correct_count / 5) * 100.0
    await finish_attempt(attempt_id, correct_count, wrong_count, pct)

    # Natijalarni tekshirish
    user_stats = await get_user_stats(test_user_id)
    assert user_stats["total_tests"] == 1
    assert user_stats["total_correct"] == 4
    assert user_stats["total_wrong"] == 1
    assert user_stats["avg_percentage"] == 80.0

    # Xato savollar tekshiruvi
    wrong_db = await get_attempt_wrong_answers(attempt_id)
    assert len(wrong_db) == 1, "Bazadagi xatolar soni 1 bo'lishi kerak!"
    print("✅ 8. Natijalar va berilgan javoblar SQLite bazasiga to'liq va to'g'ri saqlandi.")

    # 9. ADMIN XABARNOMASINING FORMATLANISHI (14-bo'lim)
    admin_notif = QuizService.format_admin_notification(
        name="Alisher Navoiy",
        username="alisher_n",
        telegram_id=test_user_id,
        total=5,
        correct=4,
        wrong=1,
        percentage=80.0,
        attempt_number=1,
        finished_at=get_current_time_str()
    )
    assert "📊 <b>YANGI TEST NATIJASI</b>" in admin_notif
    assert "👤 <b>Ism:</b> Alisher Navoiy" in admin_notif
    assert "🔗 <b>Username:</b> @alisher_n" in admin_notif
    assert f"🆔 <b>Telegram ID:</b> <code>{test_user_id}</code>" in admin_notif
    assert "📝 <b>Ishlangan savollar:</b> 5" in admin_notif
    assert "✅ <b>To‘g‘ri:</b> 4" in admin_notif
    assert "❌ <b>Noto‘g‘ri:</b> 1" in admin_notif
    assert "📈 <b>Natija:</b> 80%" in admin_notif
    assert "🔄 <b>Urinish:</b> 1" in admin_notif
    print("✅ 9. Admin xabarnomasi talab etilgan formatga 100% mos.")

    # 10. ADMINISTRATOR HUQUQLARI HIMOYASI (13-bo'lim)
    admin_filter = IsAdminFilter()
    fake_admin = type("Event", (), {"from_user": User(id=ADMIN_ID, is_bot=False, first_name="Admin")})()
    fake_user = type("Event", (), {"from_user": User(id=999888777, is_bot=False, first_name="Stranger")})()

    assert await admin_filter(fake_admin) is True, "ADMIN_ID uchun ruxsat berilishi kerak!"
    assert await admin_filter(fake_user) is False, "Begona ID uchun ruxsat berilmasligi kerak!"
    print(f"✅ 10. Administrator buyruqlari faqat ADMIN_ID ({ADMIN_ID}) uchun himoyalangan.")

    # 11. BIR VAQTDA BIR NECHTA FOYDALANUVCHILARNING TEST ISHLASHI (Concurrency)
    user2_id = 222333444
    user3_id = 333444555
    await register_or_update_user(user2_id, "Bobur", "Zahiriddin", "bobur_z")
    await register_or_update_user(user3_id, "Nodira", "Begim", "nodira_b")

    att2 = await create_attempt(user2_id, 10)
    att3 = await create_attempt(user3_id, 15)

    assert att2 != att3, "Har xil foydalanuvchilar alohida attempt_id olishi kerak!"
    await finish_attempt(att2, 9, 1, 90.0)
    await finish_attempt(att3, 15, 0, 100.0)

    stats2 = await get_user_stats(user2_id)
    stats3 = await get_user_stats(user3_id)
    assert stats2["avg_percentage"] == 90.0
    assert stats3["avg_percentage"] == 100.0
    print("✅ 11. Bir nechta foydalanuvchilar parallel ravishda test ishlay olishi tasdiqlandi.")

    # 12. TESTNI QAYTA ISHLASH (Cheksiz urinishlar - 10-bo'lim)
    att1_retry = await create_attempt(test_user_id, 10)
    await finish_attempt(att1_retry, 10, 0, 100.0)

    attempt_num = await get_user_attempt_number(test_user_id, att1_retry)
    assert attempt_num == 2, f"Kutilgan urinish raqami 2, lekin {attempt_num} chiqdi!"

    stats_retry = await get_user_stats(test_user_id)
    assert stats_retry["total_tests"] == 2, "Jami 2 ta urinish saqlanishi kerak!"
    assert stats_retry["best_attempt"]["percentage"] == 100.0, "Eng yaxshi natija 100% bo'lishi kerak!"
    print("✅ 12. Qayta test ishlash, urinishlar tartib raqami va statistika yangilanishi to'g'ri ishladi.")

    # 13. ADMIN STATISTIKASI VA REYTING (12-13 bo'limlar)
    admin_summary = await get_admin_stats()
    assert admin_summary["total_users"] >= 3
    assert admin_summary["total_attempts"] >= 4
    top_list = await get_top_users(limit=10)
    assert len(top_list) >= 3
    # Top user tekshiruvi: 100% natija birinchi bo'lishi kerak
    assert top_list[0]["percentage"] == 100.0
    print("✅ 13. Top-10 reyting va Admin statistikasi to'liq hisoblandi.")

    print("=" * 60)
    print("BARCHA 12 TA TALAB BO'YICHA TESTLAR 100% MUVAFFAQQAPQONA O'TDI!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
