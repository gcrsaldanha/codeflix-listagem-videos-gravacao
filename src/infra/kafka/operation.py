from enum import StrEnum


class Operation(StrEnum):
    CREATE = "c"
    UPDATE = "u"
    DELETE = "d"
    READ = "r"
