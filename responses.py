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
    known_flags = {'g', 'gnor' 'help'}
    flags = set()
    
    parts = lowered[len('dice '):].strip().split()
    
    dice_str = None
    for part in parts:
        if part in known_flags:
            flags.add(part)
        else:
            dice_str = part
            break
    
    show_only_graph: bool = 'gnor' in flags
    show_graph: bool = ('g' in flags) or show_only_graph
    help: bool = 'help'

    if help:
        return Response('Usage examples: \n'
                        '```'
                        '"dice 1d4"      - rolls one 4-sided dice.\n'
                        '"dice g 4d6"    - rolls the dice and shows a probability graph and your result.\n'
                        '"dice 2d8"      - rolls two 8-sided dice.\n'
                        '"dice gnor 5d4" - only shows the probability graph of the dice.\n'
                        '```')

    if not is_valid_dice_str(dice_str):
        return Response('Not a valid dice string. Correct example: "dice 1d4", "dice 12d8"')
    


    try:
        dice_to_roll: DiceToRoll = get_dice_to_roll(dice_str=dice_str)

        if dice_within_reasonable_limit(dice_to_roll=dice_to_roll):
            result = None
            result_for_graph = None
            message: str
            
            result:  DiceOutcome = decide_outcome_of_dice(dice_to_roll=dice_to_roll)

            diceProbability: DiceProbability = determine_probability (dice_to_roll=dice_to_roll, specific_result=result) 
            formatted_percentage: str = f"{diceProbability._probability:.2%}"
            
            if not show_only_graph:
                message: str         = f'{dice_str} RESULT: **{result._outcome}** ({formatted_percentage})'
            else:
                message: str = f"{dice_str} probability distribution:"
            
            if show_graph:
                result_for_graph = None if show_only_graph else result._outcome
                graph = make_probability_graph(diceProbability._distribution, result_for_graph).probability_graph
                return Response(message=message,
                                file=File(graph,
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
