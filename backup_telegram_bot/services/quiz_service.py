import json
import logging
import random
from typing import List, Dict, Any, Optional
from config import QUESTIONS_FILE

logger = logging.getLogger(__name__)


class QuizService:
    _questions_cache: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def load_questions(cls) -> List[Dict[str, Any]]:
        """Savollar bazasini JSON fayldan xotiraga yuklaydi."""
        if cls._questions_cache is None:
            try:
                with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
                    cls._questions_cache = json.load(f)
                logger.info("Jami %d ta savol JSON fayldan yuklandi.", len(cls._questions_cache))
            except Exception as e:
                logger.error("Savollarni yuklashda xatolik: %s", e)
                raise
        return cls._questions_cache

    @classmethod
    def get_total_questions_count(cls) -> int:
        """Mavjud jami savollar sonini qaytaradi."""
        return len(cls.load_questions())

    @classmethod
    def generate_quiz(cls, count: int) -> List[Dict[str, Any]]:
        """
        Belgilangan sondagi savollarni tasodifiy tanlaydi,
        savollar tartibini va har bir savolning A, B, C, D variantlarini
        tasodifiy aralashtiradi. To'g'ri javob matni saqlanib qoladi.
        """
        all_questions = cls.load_questions()
        total_available = len(all_questions)

        if count < 1 or count > total_available:
            raise ValueError(f"Savollar soni 1 va {total_available} oralig'ida bo'lishi kerak.")

        # 1. Savollarni takrorlanmasdan tasodifiy tanlash va aralashtirish
        selected_questions = random.sample(all_questions, count)

        prepared_quiz = []
        labels = ["A", "B", "C", "D"]

        for q in selected_questions:
            orig_options = list(q["options"])
            orig_correct_idx = q["correct_index"]
            correct_text = orig_options[orig_correct_idx]

            # 2. Variantlarni alohida aralashtirish
            shuffled_options = list(orig_options)
            random.shuffle(shuffled_options)

            # 3. Yangi to'g'ri javob harfini va variantlar xaritasini aniqlash
            new_correct_idx = shuffled_options.index(correct_text)
            correct_letter = labels[new_correct_idx]

            options_dict = {
                labels[i]: shuffled_options[i] for i in range(len(labels))
            }

            prepared_quiz.append({
                "id": q["id"],
                "question": q["question"],
                "options": options_dict,
                "correct_letter": correct_letter,
                "correct_text": correct_text
            })

        return prepared_quiz

    @staticmethod
    def format_question_text(question_item: Dict[str, Any], current_idx: int, total_count: int) -> str:
        """
        7-bo'lim talabiga binoan savol matnini formatlaydi:
        📚 IQTISODIY TAHLIL

        ❓ Savol 1 / 20

        [ SAVOL MATNI ]

        A) Variant 1

        B) Variant 2

        C) Variant 3

        D) Variant 4
        """
        q_text = question_item["question"]
        opts = question_item["options"]

        lines = [
            "📚 <b>IQTISODIY TAHLIL</b>",
            "",
            f"❓ <b>Savol {current_idx} / {total_count}</b>",
            "",
            f"<b>{q_text}</b>",
            "",
            f"A) {opts['A']}",
            "",
            f"B) {opts['B']}",
            "",
            f"C) {opts['C']}",
            "",
            f"D) {opts['D']}"
        ]
        return "\n".join(lines)

    @staticmethod
    def format_quiz_result(
        participant_name: str,
        total: int,
        correct: int,
        wrong: int,
        percentage: float
    ) -> str:
        """
        9-bo'lim talabiga binoan yakuniy natijani formatlaydi:
        🏆 TEST YAKUNLANDI!

        👤 Ishtirokchi: [Ism]

        📊 Umumiy natija: 17 / 20

        ✅ To‘g‘ri javoblar: 17

        ❌ Noto‘g‘ri javoblar: 3

        📈 Natija: 85%
        """
        formatted_pct = int(percentage) if percentage.is_integer() else round(percentage, 1)
        lines = [
            "🏆 <b>TEST YAKUNLANDI!</b>",
            "",
            f"👤 <b>Ishtirokchi:</b> {participant_name}",
            "",
            f"📊 <b>Umumiy natija:</b> {correct} / {total}",
            "",
            f"✅ <b>To‘g‘ri javoblar:</b> {correct}",
            "",
            f"❌ <b>Noto‘g‘ri javoblar:</b> {wrong}",
            "",
            f"📈 <b>Natija:</b> {formatted_pct}%"
        ]
        return "\n".join(lines)

    @staticmethod
    def format_wrong_answers_blocks(wrong_list: List[Dict[str, Any]]) -> List[str]:
        """
        Foydalanuvchi xato qilgan savollarni Telegram limiti (4096 belgi)
        bo'yicha sahifalarga ajratib formatlaydi.
        """
        if not wrong_list:
            return []

        header = "📝 <b>Xato qilingan savollar tahlili:</b>\n\n"
        blocks = []
        current_block = header

        for idx, item in enumerate(wrong_list, 1):
            q_text = item.get("question", "")
            user_ans = item.get("selected", "")
            corr_ans = item.get("correct", "")

            entry = (
                f"<b>{idx}. {q_text}</b>\n"
                f"❌ <i>Sizning javobingiz:</i> {user_ans}\n"
                f"✅ <i>To‘g‘ri javob:</i> {corr_ans}\n\n"
            )

            if len(current_block) + len(entry) > 3800:
                blocks.append(current_block.strip())
                current_block = entry
            else:
                current_block += entry

        if current_block.strip():
            blocks.append(current_block.strip())

        return blocks

    @staticmethod
    def format_admin_notification(
        name: str,
        username: Optional[str],
        telegram_id: int,
        total: int,
        correct: int,
        wrong: int,
        percentage: float,
        attempt_number: int,
        finished_at: str
    ) -> str:
        """
        14-bo'lim talabiga binoan admin uchun xabarnoma matnini shakllantiradi:
        📊 YANGI TEST NATIJASI

        👤 Ism: [Ism]
        🔗 Username: [Username]
        🆔 Telegram ID: [ID]

        📝 Ishlangan savollar: 20
        ✅ To‘g‘ri: 17
        ❌ Noto‘g‘ri: 3

        📈 Natija: 85%

        🔄 Urinish: 2

        📅 Sana: [Sana va vaqt]
        """
        formatted_pct = int(percentage) if percentage.is_integer() else round(percentage, 1)
        username_str = f"@{username}" if username else "Mavjud emas"

        lines = [
            "📊 <b>YANGI TEST NATIJASI</b>",
            "",
            f"👤 <b>Ism:</b> {name}",
            f"🔗 <b>Username:</b> {username_str}",
            f"🆔 <b>Telegram ID:</b> <code>{telegram_id}</code>",
            "",
            f"📝 <b>Ishlangan savollar:</b> {total}",
            f"✅ <b>To‘g‘ri:</b> {correct}",
            f"❌ <b>Noto‘g‘ri:</b> {wrong}",
            "",
            f"📈 <b>Natija:</b> {formatted_pct}%",
            "",
            f"🔄 <b>Urinish:</b> {attempt_number}",
            "",
            f"📅 <b>Sana:</b> {finished_at}"
        ]
        return "\n".join(lines)

