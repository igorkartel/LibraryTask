from enum import Enum


class PenaltyEnum(float, Enum):
    DAILY_OVERDUE = 0.01
    BOOK_DAMAGE = 0.02
    BOOK_LOST = 30.00
