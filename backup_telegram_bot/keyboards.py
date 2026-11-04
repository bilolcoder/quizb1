from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu Reply tugmalari."""
    keyboard = [
        [KeyboardButton(text="🚀 Testni boshlash")],
        [KeyboardButton(text="📊 Mening natijalarim"), KeyboardButton(text="🏆 Reyting")],
        [KeyboardButton(text="ℹ️ Bot haqida")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Kerakli bo‘limni tanlang..."
    )


def get_quiz_count_keyboard() -> ReplyKeyboardMarkup:
    """Test savollari sonini tez tanlash tugmalari."""
    keyboard = [
        [KeyboardButton(text="10"), KeyboardButton(text="20"), KeyboardButton(text="30")],
        [KeyboardButton(text="50"), KeyboardButton(text="84")],
        [KeyboardButton(text="🏠 Bosh menyu")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Savollar sonini kiriting (1-84)..."
    )


def get_quiz_options_keyboard(attempt_id: int, question_index: int) -> InlineKeyboardMarkup:
    """Savol javob variantlari uchun Inline tugmalar (A, B, C, D)."""
    buttons = [
        InlineKeyboardButton(
            text="A",
            callback_data=f"ans:{attempt_id}:{question_index}:A"
        ),
        InlineKeyboardButton(
            text="B",
            callback_data=f"ans:{attempt_id}:{question_index}:B"
        ),
        InlineKeyboardButton(
            text="C",
            callback_data=f"ans:{attempt_id}:{question_index}:C"
        ),
        InlineKeyboardButton(
            text="D",
            callback_data=f"ans:{attempt_id}:{question_index}:D"
        )
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def get_quiz_end_keyboard() -> ReplyKeyboardMarkup:
    """Test yakunlanganda chiqadigan Reply tugmalar."""
    keyboard = [
        [KeyboardButton(text="🔄 Qayta test ishlash")],
        [KeyboardButton(text="📊 Mening natijalarim"), KeyboardButton(text="🏠 Bosh menyu")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Quyidagilardan birini tanlang..."
    )


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Administrator menyusi uchun Inline tugmalar."""
    keyboard = [
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats")],
        [
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin:users:0"),
            InlineKeyboardButton(text="📝 Test natijalari", callback_data="admin:results:0")
        ],
        [InlineKeyboardButton(text="🏆 Top natijalar", callback_data="admin:top")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_pagination_keyboard(prefix: str, current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Sahifalash (Pagination) uchun tugmalar."""
    nav_row = []

    if current_page > 0:
        nav_row.append(
            InlineKeyboardButton(text="◀️ Oldingi", callback_data=f"{prefix}:{current_page - 1}")
        )

    nav_row.append(
        InlineKeyboardButton(text=f"📄 {current_page + 1}/{total_pages}", callback_data="noop")
    )

    if current_page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton(text="Keyingi ▶️", callback_data=f"{prefix}:{current_page + 1}")
        )

    back_row = [
        InlineKeyboardButton(text="🔙 Admin bosh menyusi", callback_data="admin:menu")
    ]

    return InlineKeyboardMarkup(inline_keyboard=[nav_row, back_row])

