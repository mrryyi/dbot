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
    db_instance = get_db_instance_npc_names()
    res: NameFetchResult = db_instance.get_random_untaken_name()
    if res.status != db_operation_result.SUCCESS:
        return unsuccessful_response(res)
    
    return Response(message=res.npc_name.name)

def create_response_randomtake() -> Optional[Response]:
    db_instance = get_db_instance_npc_names()
    res: NameFetchResult = db_instance.get_random_untaken_name_and_take_it()
    if res.status != db_operation_result.SUCCESS:
        return unsuccessful_response(res)
    
    return Response(message=res.npc_name.name)

def create_response_insert_name(name_to_add: str) -> Optional[Response]:
    if not name_to_add:
        return Response('Please provide a valid name to add.')
    
    db_instance = get_db_instance_npc_names()
    res: db_operation_result = db_instance.insert_singular_name(name_to_add)

    match res:
        case db_operation_result.SUCCESS:
            return Response(message=f'{name_to_add} added.')
        case db_operation_result.ALREADY_EXISTS:
            return Response(message=f'{name_to_add} already exists.')
        case db_operation_result.GENERAL_ERROR:
            return Response(message=f'General SQL error.')   

def create_response_take_name(id_to_take: int) -> Optional[Response]:
    if not id_to_take:
        return Response('Please provide a valid ID to take.')
    
    db_instance = get_db_instance_npc_names()
    res: db_operation_result = db_instance.take_name(id_to_take)

    match res.status:
        case db_operation_result.SUCCESS:
            return Response(message=f'{res.name} [{id_to_take}] taken.')
        case db_operation_result.ALREADY_TAKEN:
            return Response(message=f'{res.name} [{id_to_take}] already taken.')
        case db_operation_result.NO_QUERY_RESULT:
            return Response(message=f'Name with ID {id_to_take} not found.')
        case db_operation_result.GENERAL_ERROR:
            return Response(message=f'General SQL error.')

def create_response_untake_name(id_to_untake: int) -> Optional[Response]:
    if not id_to_untake:
        return Response('Please provide a valid ID to untake.')
    
    db_instance = get_db_instance_npc_names()
    res: db_operation_result = db_instance.untake_name(id_to_untake)

    match res.status:
        case db_operation_result.SUCCESS:
            return Response(message=f'{res.name} [{id_to_untake}] untaken.')
        case db_operation_result.ALREADY_UNTAKEN:
            return Response(message=f'{res.name} [{id_to_untake}] already untaken.')
        case db_operation_result.NO_QUERY_RESULT:
            return Response(message=f'Name with ID [{id_to_untake}] not found.')
        case db_operation_result.GENERAL_ERROR:
            return Response(message=f'General SQL error.')

def create_response_several_names(operation: str) -> Optional[Response]:
    db_instance = get_db_instance_npc_names()
    match operation:
        case 'all':
            res: NamesFetchResult = db_instance.get_all_names()
        case 'alltaken':
            res: NamesFetchResult = db_instance.get_all_taken_names()
        case 'alluntaken':
            res: NamesFetchResult = db_instance.get_all_untaken_names()
        case _:
            return
    
    if res.status != db_operation_result.SUCCESS:
        return unsuccessful_response(res)
    
    if res.npc_names:
        message = '\n'.join( f'{[npc.id]} ' + npc.name + (' (taken)' if npc.taken else '') for npc in res.npc_names)
    else:
        message = "No names available."

    return Response(message=message)

def handle_names_functionality(lowered) -> Optional[Response]:
    parts = lowered[len('name '):].strip().split()
    known_flags = {'help',
                   'add',
                   'take',
                   'untake'
                   'random',
                   'randomtake',
                   'all',
                   'alltaken',
                   'alluntaken',
                   }

    flags = set()
    for part in parts:
        if part in known_flags:
            flags.add(part)
    
    help: bool                                = 'help' in flags
    add: bool                                 = 'add' in flags
    take: bool                                = 'take' in flags
    untake: bool                              = 'untake' in flags
    get_random_untaken_name: bool             = 'random' in flags
    get_random_untaken_name_and_take_it: bool = 'randomtake' in flags
    get_all_names: bool                       = 'all' in flags 
    get_all_taken_names: bool                 = 'alltaken' in flags 
    get_all_untaken_names: bool               = 'alluntaken' in flags 
    
    if len(flags) > 1:
        return Response('Only use one flag at a time. Type "name help" for help.')

    if help:
        return Response('Usage examples: \n'
                        '```'
                        '"name add Bert Randman" - Adds "Bert Randman" as an untaken name\n'
                        '"name take 32"          - takes the name with ID 32.\n'
                        '"name untake 57"        - untakes the name with ID 57.\n'
                        '"name random"           - get a random untaken name.\n'
                        '"name randomtake"       - get a random untaken name and take it.\n'
                        '"name all"              - gets all names.\n'
                        '"name alltaken"         - gets all taken names.\n'
                        '"name alluntaken"       - gets all untaken names.\n'
                        '```')
    
    try:
        if add:
            return create_response_insert_name(' '.join(parts[1:]))

        if (take or untake):
            if len(parts) != 2 or not parts[1].isdigit():
                return Response('Please provide a valid ID to take.')
            else:
                return create_response_take_name(parts[1]) if take else create_response_untake_name(parts[1])
        
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
