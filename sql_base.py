from enum import IntEnum
from dataclasses import dataclass

class db_operation_result(IntEnum):
    SUCCESS = 0
    GENERAL_ERROR = 1
    ALREADY_EXISTS = 2
    NO_QUERY_RESULT = 3
    # Error code for attempting to take a name that is already taken
    ALREADY_TAKEN = 4
    ALREADY_UNTAKEN = 5

@dataclass
class FetchResult:
    status: db_operation_result
    error_message: str = None