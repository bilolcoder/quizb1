import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
import aiosqlite
from config import DATABASE_PATH

logger = logging.getLogger(__name__)


def get_current_time_str() -> str:
    """Hozirgi vaqtni YYYY-MM-DD HH:MM:SS formatida qaytaradi."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def init_db() -> None:
    """Ma'lumotlar bazasi jadvallarini yaratadi."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Crash-resilience va yuqori tezlik uchun WAL rejimi
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("PRAGMA synchronous=NORMAL;")

        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                first_name TEXT,
                last_name TEXT,
                username TEXT,
                created_at TEXT NOT NULL,
                last_active TEXT NOT NULL
            );
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                correct_answers INTEGER DEFAULT 0,
                wrong_answers INTEGER DEFAULT 0,
                percentage REAL DEFAULT 0.0,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(telegram_id) ON DELETE CASCADE
            );
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS attempt_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attempt_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                selected_answer TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                FOREIGN KEY (attempt_id) REFERENCES attempts(id) ON DELETE CASCADE
            );
        """)

        await db.execute("CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_attempts_user_id ON attempts(user_id);")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_attempt_answers_attempt_id ON attempt_answers(attempt_id);")
        await db.commit()
    logger.info("Database jadvallari muvaffaqiyatli ishga tushirildi.")


async def register_or_update_user(
    telegram_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    username: Optional[str] = None
) -> Dict[str, Any]:
    """Foydalanuvchini bazaga kiritadi yoki faolligini yangilaydi."""
    now = get_current_time_str()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            user = await cursor.fetchone()

        if user:
            await db.execute("""
                UPDATE users
                SET first_name = ?, last_name = ?, username = ?, last_active = ?
                WHERE telegram_id = ?
            """, (first_name, last_name, username, now, telegram_id))
            await db.commit()
            return {"user": dict(user), "is_new": False}
        else:
            await db.execute("""
                INSERT INTO users (telegram_id, first_name, last_name, username, created_at, last_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (telegram_id, first_name, last_name, username, now, now))
            await db.commit()
            async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
                new_user = await cursor.fetchone()
            return {"user": dict(new_user) if new_user else {}, "is_new": True}


async def update_user_activity(telegram_id: int) -> None:
    """Foydalanuvchining oxirgi faollik vaqtini yangilaydi."""
    now = get_current_time_str()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE users SET last_active = ? WHERE telegram_id = ?", (now, telegram_id))
        await db.commit()


async def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Telegram ID bo'yicha foydalanuvchini oladi."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def create_attempt(user_id: int, total_questions: int) -> int:
    """Yangi test urinishini yaratadi va uning ID sini qaytaradi."""
    now = get_current_time_str()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO attempts (user_id, total_questions, correct_answers, wrong_answers, percentage, started_at)
            VALUES (?, ?, 0, 0, 0.0, ?)
        """, (user_id, total_questions, now))
        await db.commit()
        return cursor.lastrowid


async def save_attempt_answer(
    attempt_id: int,
    question_id: int,
    selected_answer: str,
    correct_answer: str,
    is_correct: bool
) -> None:
    """Savolga berilgan javobni saqlaydi."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO attempt_answers (attempt_id, question_id, selected_answer, correct_answer, is_correct)
            VALUES (?, ?, ?, ?, ?)
        """, (attempt_id, question_id, selected_answer, correct_answer, 1 if is_correct else 0))
        await db.commit()


async def finish_attempt(
    attempt_id: int,
    correct_answers: int,
    wrong_answers: int,
    percentage: float
) -> None:
    """Urinishni yakunlaydi va natijalarni saqlaydi."""
    now = get_current_time_str()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE attempts
            SET correct_answers = ?, wrong_answers = ?, percentage = ?, finished_at = ?
            WHERE id = ?
        """, (correct_answers, wrong_answers, round(percentage, 2), now, attempt_id))
        await db.commit()


async def get_user_attempt_number(user_id: int, attempt_id: int) -> int:
    """Foydalanuvchining ayni paytdagi urinish tartib raqamini qaytaradi."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("""
            SELECT COUNT(*) FROM attempts
            WHERE user_id = ? AND id <= ?
        """, (user_id, attempt_id)) as cursor:
            res = await cursor.fetchone()
            return res[0] if res else 1


async def get_user_stats(telegram_id: int) -> Dict[str, Any]:
    """Foydalanuvchining barcha statistik ma'lumotlarini hisoblaydi."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Jami tugallangan testlar soni
        async with db.execute("""
            SELECT COUNT(*) as count FROM attempts
            WHERE user_id = ? AND finished_at IS NOT NULL
        """, (telegram_id,)) as cursor:
            total_tests = (await cursor.fetchone())["count"]

        if total_tests == 0:
            return {"total_tests": 0}

        # Eng yaxshi natija
        async with db.execute("""
            SELECT total_questions, correct_answers, wrong_answers, percentage
            FROM attempts
            WHERE user_id = ? AND finished_at IS NOT NULL
            ORDER BY percentage DESC, correct_answers DESC, id ASC
            LIMIT 1
        """, (telegram_id,)) as cursor:
            best_row = await cursor.fetchone()
            best_attempt = dict(best_row) if best_row else None

        # Oxirgi natija
        async with db.execute("""
            SELECT total_questions, correct_answers, wrong_answers, percentage, finished_at
            FROM attempts
            WHERE user_id = ? AND finished_at IS NOT NULL
            ORDER BY id DESC
            LIMIT 1
        """, (telegram_id,)) as cursor:
            latest_row = await cursor.fetchone()
            latest_attempt = dict(latest_row) if latest_row else None

        # O'rtacha foiz, jami to'g'ri va noto'g'ri javoblar
        async with db.execute("""
            SELECT 
                AVG(percentage) as avg_pct,
                SUM(correct_answers) as sum_correct,
                SUM(wrong_answers) as sum_wrong
            FROM attempts
            WHERE user_id = ? AND finished_at IS NOT NULL
        """, (telegram_id,)) as cursor:
            summary_row = await cursor.fetchone()

        return {
            "total_tests": total_tests,
            "best_attempt": best_attempt,
            "latest_attempt": latest_attempt,
            "avg_percentage": round(summary_row["avg_pct"], 1) if summary_row and summary_row["avg_pct"] is not None else 0.0,
            "total_correct": summary_row["sum_correct"] if summary_row and summary_row["sum_correct"] is not None else 0,
            "total_wrong": summary_row["sum_wrong"] if summary_row and summary_row["sum_wrong"] is not None else 0,
        }


async def get_top_users(limit: int = 10) -> List[Dict[str, Any]]:
    """Eng yaxshi natijaga ega foydalanuvchilar reytingini qaytaradi."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = """
            WITH RankedAttempts AS (
                SELECT 
                    a.user_id,
                    a.total_questions,
                    a.correct_answers,
                    a.percentage,
                    u.first_name,
                    u.last_name,
                    u.username,
                    ROW_NUMBER() OVER (
                        PARTITION BY a.user_id 
                        ORDER BY a.percentage DESC, a.correct_answers DESC, a.id ASC
                    ) as rn
                FROM attempts a
                JOIN users u ON a.user_id = u.telegram_id
                WHERE a.finished_at IS NOT NULL
            )
            SELECT * FROM RankedAttempts 
            WHERE rn = 1 
            ORDER BY percentage DESC, correct_answers DESC 
            LIMIT ?
        """
        async with db.execute(query, (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def get_admin_stats() -> Dict[str, Any]:
    """Administrator uchun umumiy statistikani hisoblaydi."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row

        # 1. Jami foydalanuvchilar soni
        async with db.execute("SELECT COUNT(*) as count FROM users") as cursor:
            total_users = (await cursor.fetchone())["count"]

        # 2. Test boshlagan foydalanuvchilar soni
        async with db.execute("SELECT COUNT(DISTINCT user_id) as count FROM attempts") as cursor:
            users_started = (await cursor.fetchone())["count"]

        # 3. Testni tugatgan foydalanuvchilar soni
        async with db.execute("SELECT COUNT(DISTINCT user_id) as count FROM attempts WHERE finished_at IS NOT NULL") as cursor:
            users_finished = (await cursor.fetchone())["count"]

        # 4. Jami urinishlar soni
        async with db.execute("SELECT COUNT(*) as count FROM attempts") as cursor:
            total_attempts = (await cursor.fetchone())["count"]

        # 5. Tugallangan urinishlar soni
        async with db.execute("SELECT COUNT(*) as count FROM attempts WHERE finished_at IS NOT NULL") as cursor:
            finished_attempts = (await cursor.fetchone())["count"]

        # 6. Jami berilgan javoblar soni
        async with db.execute("SELECT COUNT(*) as count FROM attempt_answers") as cursor:
            total_answers = (await cursor.fetchone())["count"]

        # 7. O'rtacha natija foizi
        async with db.execute("SELECT AVG(percentage) as avg_pct FROM attempts WHERE finished_at IS NOT NULL") as cursor:
            res = await cursor.fetchone()
            avg_percentage = round(res["avg_pct"], 1) if res and res["avg_pct"] is not None else 0.0

        return {
            "total_users": total_users,
            "users_started": users_started,
            "users_finished": users_finished,
            "total_attempts": total_attempts,
            "finished_attempts": finished_attempts,
            "total_answers": total_answers,
            "avg_percentage": avg_percentage,
        }


async def get_users_count() -> int:
    """Jami foydalanuvchilar soni."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            res = await cursor.fetchone()
            return res[0] if res else 0


async def get_all_users(offset: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
    """Foydalanuvchilar ro'yxatini sahifalab qaytaradi."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = """
            SELECT 
                u.id,
                u.telegram_id,
                u.first_name,
                u.last_name,
                u.username,
                u.created_at,
                u.last_active,
                COUNT(a.id) as tests_count
            FROM users u
            LEFT JOIN attempts a ON u.telegram_id = a.user_id AND a.finished_at IS NOT NULL
            GROUP BY u.id
            ORDER BY u.id DESC
            LIMIT ? OFFSET ?
        """
        async with db.execute(query, (limit, offset)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def get_attempts_count() -> int:
    """Jami urinishlar soni."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM attempts") as cursor:
            res = await cursor.fetchone()
            return res[0] if res else 0


async def get_all_attempts(offset: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
    """Barcha urinishlarni foydalanuvchi ma'lumotlari bilan sahifalab qaytaradi."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = """
            SELECT 
                a.id as attempt_id,
                a.user_id,
                a.total_questions,
                a.correct_answers,
                a.wrong_answers,
                a.percentage,
                a.started_at,
                a.finished_at,
                u.first_name,
                u.last_name,
                u.username,
                (
                    SELECT COUNT(*) 
                    FROM attempts a2 
                    WHERE a2.user_id = a.user_id AND a2.id <= a.id
                ) as attempt_number
            FROM attempts a
            JOIN users u ON a.user_id = u.telegram_id
            ORDER BY a.id DESC
            LIMIT ? OFFSET ?
        """
        async with db.execute(query, (limit, offset)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def get_attempt_wrong_answers(attempt_id: int) -> List[Dict[str, Any]]:
    """Urinishdagi barcha xato javoblarni qaytaradi."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT question_id, selected_answer, correct_answer
            FROM attempt_answers
            WHERE attempt_id = ? AND is_correct = 0
            ORDER BY id ASC
        """, (attempt_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

