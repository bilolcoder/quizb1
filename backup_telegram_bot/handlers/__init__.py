from aiogram import Dispatcher
from .admin import router as admin_router
from .start import router as start_router
from .quiz import router as quiz_router
from .results import router as results_router


def setup_routers(dp: Dispatcher) -> None:
    """Barcha routerlarni ro'yxatdan o'tkazadi."""
    dp.include_router(admin_router)
    dp.include_router(start_router)
    dp.include_router(quiz_router)
    dp.include_router(results_router)

