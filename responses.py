from dice import *
from log import *
from typing import Optional
from discord import File

@dataclass
class Response:
    message: str
    file: Optional[File] = None

def get_response(user_input: str) -> Response:
    lowered: str = user_input.lower()

    # dice thing
    if lowered.startswith('dice '):
        dice_str = lowered[len('dice '):].strip()
        if is_valid_dice_str(dice_str):
            try:
                result: DiceOutcome       = get_dice_roll(dice_str)
                formatted_percentage: str = f"{result.probability:.2%}"
                message                   = f'{dice_str} RESULT: **{result.total_roll}** ({formatted_percentage})'
                if result.probability_graph:
                    return Response(message=message,
                                    file=File(result.probability_graph,
                                              filename='probability_distribution.png'))
                else:
                    return Response(message=message)
            except Exception as e:
                log_exception_local(e)
        else:
            return 'Not a valid dice string. Correct example: "ddice 1d4", "ddice 12d8"'
    