from dataclasses import dataclass
from dice import *
from npc_names import *
from log import *
from typing import Optional, List, Tuple
from discord import File

@dataclass
class Response:
    message: str
    file: Optional[File] = None

#region dice
def parse_flags_and_dice_str(parts: List[str]) -> Tuple[List[str], str]:
    # Assume all parts except the last one are flags, and the last one is the dice string
    flags = parts[:-1]
    dice_str = parts[-1]
    return flags, dice_str

def handle_dice_functionality(lowered: str) -> Optional[Response]:
    known_flags = {'g', 'gnor', 'help'}
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
    show_graph: bool      = ('g' in flags) or show_only_graph
    help: bool            = 'help' in flags

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
                message: str = f'{dice_str} RESULT: **{result._outcome}** ({formatted_percentage})'
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
#endregion


#region npc_names

def unsuccessful_response(res: FetchResult) -> Optional[Response]:
    nicer_status_text: str
    match res.status:
        case db_operation_result.GENERAL_ERROR:
            nicer_status_text = 'General SQL error.'
        case db_operation_result.ALREADY_EXISTS:
            nicer_status_text = 'Already exists.'
        case db_operation_result.NO_QUERY_RESULT:
            nicer_status_text = 'No data found.'
    
    message: str
    if res.error_message is None:
        message: str = f'Request failed. Status: {nicer_status_text}'
    else:
        message: str = f'Request failed. Status: {nicer_status_text} with error {res.error_message}'   
    return Response(message=message)

def create_response_random() -> Optional[Response]:
    res: NameFetchResult = get_random_untaken_name()
    if res.status != db_operation_result.SUCCESS:
        return unsuccessful_response(res)
    
    return Response(message=res.npc_name.name)

def create_response_randomtake() -> Optional[Response]:
    res: NameFetchResult = get_random_untaken_name_and_take_it()
    if res.status != db_operation_result.SUCCESS:
        return unsuccessful_response(res)
    
    return Response(message=res.npc_name.name)

def create_response_insert_name(name_to_add: str) -> Optional[Response]:
    if not name_to_add:
        return Response('Please provide a valid name to add.')
    
    res: db_operation_result = insert_singular_name(name_to_add)

    match res:
        case db_operation_result.SUCCESS:
            return Response(message=f'{name_to_add} added.')
        case db_operation_result.ALREADY_EXISTS:
            return Response(message=f'{name_to_add} already exists.')
        case db_operation_result.GENERAL_ERROR:
            return Response(message=f'General SQL error.')   

def create_response_several_names(operation: str) -> Optional[Response]:
    match operation:
        case 'all':
            res: NamesFetchResult = get_all_names()
        case 'alltaken':
            res: NamesFetchResult = get_all_taken_names()
        case 'alluntaken':
            res: NamesFetchResult = get_all_untaken_names()
        case _:
            return
    
    if res.status != db_operation_result.SUCCESS:
        return unsuccessful_response(res)
    
    if res.npc_names:
        message = '\n'.join(npc.name + (' (taken)' if npc.taken else '') for npc in res.npc_names)
    else:
        message = "No names available."

    return Response(message=message)
    

def handle_names_functionality(lowered) -> Optional[Response]:
    parts = lowered[len('name '):].strip().split()
    known_flags = {'add',
                   'all',
                   'alltaken',
                   'alluntaken',
                   'random',
                   'randomtake',
                   'help'}

    flags = set()
    for part in parts:
        if part in known_flags:
            flags.add(part)
    
    help: bool                                = 'help' in flags
    add: bool                                 = 'add' in flags
    get_random_untaken_name: bool             = 'random' in flags
    get_random_untaken_name_and_take_it: bool = 'randomtake' in flags
    get_all_names: bool                       = 'all' in flags 
    get_all_taken_names: bool                 = 'alltaken' in flags 
    get_all_untaken_names: bool               = 'alluntaken' in flags 
    
    if len(flags) > 1:
        return Response('Only use one flag at a time. Type "name help" for help.')
    
    if add:
         # Everything after add is the name
        name_to_add = ' '.join(parts[1:]).strip().title()
        return create_response_insert_name(name_to_add)

    if help:
        return Response('Usage examples: \n'
                        '```'
                        '"name random" - get a random untaken name.\n'
                        '"name all"    - gets all untaken names.\n'
                        '"name add Bert Randman" - Adds "Bert Randman" as an untaken name'
                        '```')
    
    try:
        if get_random_untaken_name:
            return create_response_random()
        if get_random_untaken_name_and_take_it:
            return create_response_randomtake()
        
        if get_all_names:
            return create_response_several_names('all')
        if get_all_taken_names:
            return create_response_several_names('alltaken')
        if get_all_untaken_names:
            return create_response_several_names('alluntaken')
    except Exception as e:
        log_exception_local(e)

#endregion

def get_response(user_input: str) -> Optional[Response]:
    lowered: str = user_input.lower()

    if lowered.startswith('dice '):
        return handle_dice_functionality(lowered)
    
    if lowered.startswith('name '):
        return handle_names_functionality(lowered)
    return None
