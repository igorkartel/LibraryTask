from enum import Enum


class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    LIBRARIAN = "librarian"
