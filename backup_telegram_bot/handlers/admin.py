import logging
from math import ceil
from typing import Union
from aiogram import Router, F
from aiogram.filters import Command, Filter
from aiogram.types import Message, CallbackQuery, TelegramObject

from config import ADMIN_ID
from database import (
    get_admin_stats,
    get_all_users,
    get_users_count,
    get_all_attempts,
    get_attempts_count,
    get_top_users
)
from keyboards import get_admin_keyboard, get_pagination_keyboard

logger = logging.getLogger(__name__)

router = Router(name="admin_router")


class IsAdminFilter(Filter):
    async def __call__(self, event: TelegramObject) -> bool:
        user = getattr(event, "from_user", None)
        return bool(user and user.id == ADMIN_ID)


# Barcha admin handlerlar uchun filtr
admin_only = IsAdminFilter()


# Ruxsatsiz foydalanuvchilar uchun xabar
@router.message(Command(commands=["admin", "stats", "users", "results"]), ~admin_only)
async def unauthorized_access(message: Message):
    await message.answer("⛔️ Kechirasiz, ushbu buyruq faqat bot administratori uchun mo‘ljallangan!")


@router.message(Command("admin"), admin_only)
async def handle_admin_menu(message: Message):
    """
    13-bo'lim: Administrator boshqaruv paneli.
    """
    stats = await get_admin_stats()
    text = (
        "🛠 <b>ADMINISTRATOR BOSHQARUV PANELI</b>\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {stats['total_users']} nafar\n"
        f"🚀 <b>Test boshlaganlar:</b> {stats['users_started']} nafar\n"
        f"🏁 <b>Testni tugatganlar:</b> {stats['users_finished']} nafar\n"
        f"🔄 <b>Jami test urinishlari:</b> {stats['total_attempts']} ta\n\n"
        "Quyidagi bo‘limlardan birini tanlang:"
    )
    await message.answer(text, reply_markup=get_admin_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "admin:menu", admin_only)
async def cb_admin_menu(callback: CallbackQuery):
    stats = await get_admin_stats()
    text = (
        "🛠 <b>ADMINISTRATOR BOSHQARUV PANELI</b>\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {stats['total_users']} nafar\n"
        f"🚀 <b>Test boshlaganlar:</b> {stats['users_started']} nafar\n"
        f"🏁 <b>Testni tugatganlar:</b> {stats['users_finished']} nafar\n"
        f"🔄 <b>Jami test urinishlari:</b> {stats['total_attempts']} ta\n\n"
        "Quyidagi bo‘limlardan birini tanlang:"
    )
    try:
        await callback.message.edit_text(text, reply_markup=get_admin_keyboard(), parse_mode="HTML")
    except Exception:
        await callback.message.answer(text, reply_markup=get_admin_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.message(Command("stats"), admin_only)
@router.callback_query(F.data == "admin:stats", admin_only)
async def handle_admin_stats(event: Union[Message, CallbackQuery]):
    """
    13-bo'lim: Kengaytirilgan umumiy statistika.
    """
    stats = await get_admin_stats()
    text = (
        "📊 <b>BOTNING TO‘LIQ STATISTIKASI</b>\n\n"
        f"👥 <b>Jami ro‘yxatdan o‘tganlar:</b> {stats['total_users']} nafar\n"
        f"🚀 <b>Test boshlagan foydalanuvchilar:</b> {stats['users_started']} nafar\n"
        f"🏁 <b>Kamida 1 marta test tugatganlar:</b> {stats['users_finished']} nafar\n\n"
        f"📝 <b>Jami boshlangan urinishlar:</b> {stats['total_attempts']} ta\n"
        f"✅ <b>Tugallangan urinishlar:</b> {stats['finished_attempts']} ta\n"
        f"❓ <b>Jami berilgan javoblar soni:</b> {stats['total_answers']} ta\n"
        f"📈 <b>Umumiy o‘rtacha o‘zlashtirish:</b> {stats['avg_percentage']}%\n"
    )

    if isinstance(event, CallbackQuery):
        try:
            await event.message.edit_text(
                text,
                reply_markup=get_pagination_keyboard("admin:users", 0, 1),
                parse_mode="HTML"
            )
        except Exception:
            await event.message.answer(text, parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(text, parse_mode="HTML")


@router.message(Command("users"), admin_only)
async def handle_users_cmd(message: Message):
    await show_users_page(message, page=0)


@router.callback_query(F.data.startswith("admin:users:"), admin_only)
async def handle_users_callback(callback: CallbackQuery):
    parts = callback.data.split(":")
    page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
    await show_users_page(callback, page=page)
    await callback.answer()


async def show_users_page(event: Union[Message, CallbackQuery], page: int = 0):
    """
    13-bo'lim: Foydalanuvchilar ro'yxatini sahifalab ko'rsatish.
    """
    limit = 10
    total_users = await get_users_count()

    if total_users == 0:
        msg = "👥 Hozircha botda foydalanuvchilar mavjud emas."
        if isinstance(event, CallbackQuery):
            await event.message.answer(msg)
        else:
            await event.answer(msg)
        return

    total_pages = max(1, ceil(total_users / limit))
    page = max(0, min(page, total_pages - 1))
    offset = page * limit

    users = await get_all_users(offset=offset, limit=limit)

    lines = [f"👥 <b>FOYDALANUVCHILAR RO‘YXATI (Jami: {total_users})</b>\n"]

    for idx, u in enumerate(users, start=offset + 1):
        f_name = u.get("first_name") or ""
        l_name = u.get("last_name") or ""
        full_name = f"{f_name} {l_name}".strip() or "Nomsiz"
        username_str = f"@{u['username']}" if u.get("username") else "Yo‘q"
        tg_id = u["telegram_id"]
        tests_count = u.get("tests_count", 0)
        created_at = u.get("created_at", "-")
        last_active = u.get("last_active", "-")

        lines.append(
            f"<b>{idx}. {full_name}</b>\n"
            f"   🆔 ID: <code>{tg_id}</code> | 🔗 {username_str}\n"
            f"   📝 Testlar soni: {tests_count} ta\n"
            f"   📅 Ro‘yxatdan o‘tgan: {created_at}\n"
            f"   ⏱ Oxirgi faollik: {last_active}\n"
        )

    text = "\n".join(lines)
    keyboard = get_pagination_keyboard("admin:users", page, total_pages)

    if isinstance(event, CallbackQuery):
        try:
            await event.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        except Exception:
            await event.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await event.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.message(Command("results"), admin_only)
async def handle_results_cmd(message: Message):
    await show_results_page(message, page=0)


@router.callback_query(F.data.startswith("admin:results:"), admin_only)
async def handle_results_callback(callback: CallbackQuery):
    parts = callback.data.split(":")
    page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
    await show_results_page(callback, page=page)
    await callback.answer()


async def show_results_page(event: Union[Message, CallbackQuery], page: int = 0):
    """
    13-bo'lim: Urinishlar tarixini sahifalab ko'rsatish.
    """
    limit = 5
    total_attempts = await get_attempts_count()

    if total_attempts == 0:
        msg = "📝 Hozircha birorta ham test urinishi amalga oshirilmagan."
        if isinstance(event, CallbackQuery):
            await event.message.answer(msg)
        else:
            await event.answer(msg)
        return

    total_pages = max(1, ceil(total_attempts / limit))
    page = max(0, min(page, total_pages - 1))
    offset = page * limit

    attempts = await get_all_attempts(offset=offset, limit=limit)

    lines = [f"📝 <b>TEST URINISHLARI TARIXI (Jami: {total_attempts})</b>\n"]

    for a in attempts:
        user_name = a.get("first_name") or "Ishtirokchi"
        username_str = f"@{a['username']}" if a.get("username") else "Yo‘q"
        pct = a.get("percentage", 0.0)
        pct_formatted = int(pct) if float(pct).is_integer() else round(pct, 1)

        lines.append(
            f"🔹 <b>Urinish #{a['attempt_id']}</b> (Foydalanuvchining {a['attempt_number']}-urinishi)\n"
            f"👤 <b>Ism:</b> {user_name} (🔗 {username_str})\n"
            f"🆔 <b>Telegram ID:</b> <code>{a['user_id']}</code>\n"
            f"📊 <b>Natija:</b> {a['correct_answers']} / {a['total_questions']} ({pct_formatted}%)\n"
            f"✅ <b>To‘g‘ri:</b> {a['correct_answers']} | ❌ <b>Noto‘g‘ri:</b> {a['wrong_answers']}\n"
            f"⏱ <b>Boshlangan:</b> {a['started_at']}\n"
            f"🏁 <b>Tugagan:</b> {a['finished_at'] or 'Tugallanmagan'}\n"
        )

    text = "\n".join(lines)
    keyboard = get_pagination_keyboard("admin:results", page, total_pages)

    if isinstance(event, CallbackQuery):
        try:
            await event.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        except Exception:
            await event.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await event.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.message(Command("top"), admin_only)
@router.callback_query(F.data == "admin:top", admin_only)
async def handle_admin_top(event: Union[Message, CallbackQuery]):
    """
    13-bo'lim: Administrator uchun batafsil top-10 reytingi.
    """
    top_users = await get_top_users(limit=10)

    if not top_users:
        msg = "🏆 Hozircha reyting mavjud emas."
        if isinstance(event, CallbackQuery):
            await event.message.answer(msg)
            await event.answer()
        else:
            await event.answer(msg)
        return

    lines = ["🏆 <b>ENG YAXSHI 10 TA NATIJA (ADMIN KO‘RINISHI)</b>\n"]
    medals = ["🥇", "🥈", "🥉"]

    for idx, item in enumerate(top_users, 1):
        medal = medals[idx - 1] if idx <= 3 else f"{idx}."
        f_name = item.get("first_name") or "Ishtirokchi"
        username_str = f"@{item['username']}" if item.get("username") else "Yo‘q"
        tg_id = item.get("user_id")
        pct = item.get("percentage", 0.0)
        pct_formatted = int(pct) if float(pct).is_integer() else round(pct, 1)
        correct = item.get("correct_answers", 0)
        total = item.get("total_questions", 0)

        lines.append(
            f"{medal} <b>{f_name}</b> (🔗 {username_str})\n"
            f"   🆔 <code>{tg_id}</code> | 📊 {correct}/{total} ({pct_formatted}%)\n"
        )

    text = "\n".join(lines)
    back_markup = get_pagination_keyboard("admin:users", 0, 1)

    if isinstance(event, CallbackQuery):
        try:
            await event.message.edit_text(text, reply_markup=back_markup, parse_mode="HTML")
        except Exception:
            await event.message.answer(text, reply_markup=back_markup, parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(text, parse_mode="HTML")


@router.callback_query(F.data == "noop")
async def cb_noop(callback: CallbackQuery):
    await callback.answer()

