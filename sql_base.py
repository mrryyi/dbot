from enum import IntEnum
from dataclasses import dataclass

class db_operation_result(IntEnum):
    SUCCESS = (0, 'Success.')
    GENERAL_ERROR = (1, 'General SQL error.')
    ALREADY_EXISTS = (2, 'Already exists.')
    NO_QUERY_RESULT = (3, 'No data found.')
    ALREADY_TAKEN = (4, 'Already taken.')
    ALREADY_UNTAKEN = (5, 'Already untaken.')

    def __new__(cls, value, message):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.status_text = message
        return obj

@dataclass
class FetchResult:
    status: db_operation_result
    error_message: str = None
