from enum import IntEnum
from dataclasses import dataclass

class db_operation_result(IntEnum):
    SUCCESS = 0
    GENERAL_ERROR = 1
    ALREADY_EXISTS = 2
    NO_QUERY_RESULT = 3

@dataclass
class FetchResult:
    status: db_operation_result
    error_message: str = None
