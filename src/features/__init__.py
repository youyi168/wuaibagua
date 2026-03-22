# Features modules
from .history.history import get_history_manager
from .favorite.favorite import get_favorite_manager
from .statistics.statistics import create_statistics_screen

__all__ = [
    'get_history_manager',
    'get_favorite_manager',
    'create_statistics_screen',
]
