from dice import *
from log import *
from typing import Optional, List, Tuple
from discord import File

@dataclass
class Response:
    message: str
    file: Optional[File] = None

def parse_flags_and_dice_str(parts: List[str]) -> Tuple[List[str], str]:
    # Assume all parts except the last one are flags, and the last one is the dice string
    flags = parts[:-1]
    dice_str = parts[-1]
    return flags, dice_str

def handle_dice_functionality(lowered: str) -> Optional[Response]:
    
    parts = lowered[len('dice '):].strip().split()
    flags, dice_str = parse_flags_and_dice_str(parts)

    if not is_valid_dice_str(dice_str):
        return Response('Not a valid dice string. Correct example: "ddice 1d4", "ddice 12d8"')
    
    try:
        dice_to_roll = get_dice_to_roll(dice_str=dice_str)
        if dice_within_reasonable_limit(dice_to_roll=dice_to_roll):
            result: DiceOutcome       = get_dice_roll(dice_to_roll=dice_to_roll)
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

def get_response(user_input: str) -> Optional[Response]:
    lowered: str = user_input.lower()

    if lowered.startswith('dice '):
        return handle_dice_functionality(lowered)

    return None
