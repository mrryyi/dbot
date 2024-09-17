from random      import randint
from dataclasses import dataclass
import re

from typing      import Optional
from collections import defaultdict
from itertools   import product
from io          import BytesIO
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

@dataclass
class DiceOutcome:
    _outcome: int

@dataclass
class DiceProbability:
    _probability: float = None
    _distribution: dict[int, float] = None

@dataclass
class DiceProbabilityGraph:
    probability_graph: Optional[BytesIO] = None

@dataclass
class DiceToRoll:
    amount_of_dice: int
    dice_value: int

def is_valid_dice_str(dice_str: str) -> bool:
    return bool(re.match(r'^\d+[dD]\d+$', dice_str))

# Not mine
def dice_probability_distribution(dice_to_roll: DiceToRoll) -> dict[int, float]:
    # Dictionary to store the frequency of each possible sum
    frequency_distribution = defaultdict(int)

    # Generate all possible outcomes using itertools.product
    outcomes = product(range(1, dice_to_roll.dice_value + 1), repeat=dice_to_roll.amount_of_dice)

    # Calculate the sum for each outcome and count its frequency
    for outcome in outcomes:
        total = sum(outcome)
        frequency_distribution[total] += 1

    # Total number of possible outcomes
    total_outcomes = dice_to_roll.dice_value ** dice_to_roll.amount_of_dice

    # Calculate the probability distribution
    probability_distribution = {sum_: freq / total_outcomes for sum_, freq in frequency_distribution.items()}
    return probability_distribution

def make_probability_graph(probability_distribution: dict[int, float], result: int = None) -> DiceProbabilityGraph:
    plt.figure(figsize=(10, 6))
    bars = plt.bar(probability_distribution.keys(), probability_distribution.values(), color='skyblue')
    plt.xlabel('Possible Result')
    plt.ylabel('Probability')
    plt.title('Probability Distribution')

    # Only highlight if the result is present.
    if result:
        # Iterate through the bars and highlight the one that matches the result
        for bar in bars:
            if bar.get_x() == result - 0.4:  # Adjust for bar width offset
                bar.set_color('orange')  # Highlight color for the result bar
                bar.set_edgecolor('black')  # Optional: set edge color for visibility

    # Uncomment to make x labels look like shit given enough x
    #plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure only integer ticks
    #plt.xticks(ticks=list(probability_distribution.keys()))  # Set all possible results as x-ticks

    # in-memory rocks.
    diceProbabilityGraph = DiceProbabilityGraph
    diceProbabilityGraph.probability_graph = BytesIO()
    plt.savefig(diceProbabilityGraph.probability_graph, format='png')
    diceProbabilityGraph.probability_graph.seek(0)
    plt.close()

    return diceProbabilityGraph


def parse_dice_str(dice_str: str) -> DiceToRoll:
    try:
        amount_of_dice, dice_value = map(int, dice_str.lower().split('d'))
        dice_to_roll = DiceToRoll(amount_of_dice=amount_of_dice, dice_value=dice_value)
    except ValueError:
        raise ValueError(f'Invalid input format of dice str "{dice_str}".')
    
    return dice_to_roll

def determine_probability(dice_to_roll, specific_result: DiceOutcome = None) -> DiceProbability:
    diceProbability = DiceProbability 
    diceProbability._distribution       = dice_probability_distribution(dice_to_roll)    
    diceProbability._probability = diceProbability._distribution.get(specific_result._outcome, 0.0)

    return diceProbability

def get_dice_to_roll(dice_str: str) -> DiceToRoll:
    dice_to_roll: DiceToRoll = parse_dice_str(dice_str)
    return dice_to_roll

def decide_outcome_of_dice(dice_to_roll: DiceToRoll) -> DiceOutcome:
    return DiceOutcome(_outcome = sum(randint(1, dice_to_roll.dice_value) for _ in range(dice_to_roll.amount_of_dice)))

def dice_within_reasonable_limit(dice_to_roll: DiceToRoll) -> bool:
    if (dice_to_roll.amount_of_dice + dice_to_roll.dice_value) >= 18:
        return False
    return True