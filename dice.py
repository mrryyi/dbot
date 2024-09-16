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
    total_roll: int
    probability: float
    probability_graph: Optional[BytesIO] = None

@dataclass
class DiceToRoll:
    amount_of_dice: int
    dice_value: int

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

def make_probability_graph(probability_distribution, result: int = None) -> BytesIO:
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
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return buf

def is_valid_dice_str(dice_str: str) -> bool:
    return bool(re.match(r'^\d+[dD]\d+$', dice_str))

def parse_dice_str(dice_str: str) -> DiceToRoll:
    try:
        amount_of_dice, dice_value = map(int, dice_str.lower().split('d'))
        dice_to_roll = DiceToRoll(amount_of_dice=amount_of_dice, dice_value=dice_value)
    except ValueError:
        raise ValueError(f'Invalid input format of dice str "{dice_str}".')
    
    return dice_to_roll

def decide_outcome_of_dice(dice_to_roll: DiceToRoll) -> DiceOutcome:

    # roll the dice
    total_roll = sum(randint(1, dice_to_roll.dice_value) for _ in range(dice_to_roll.amount_of_dice))

    probability_distribution     = dice_probability_distribution(dice_to_roll)    
    probability_of_specific_roll = probability_distribution.get(total_roll, 0.0)

    # Create a graph of the probability distribution in-memory
    probability_graph = make_probability_graph(probability_distribution, total_roll)

    dice_outcome = DiceOutcome(total_roll        = total_roll,
                               probability       = probability_of_specific_roll,
                               probability_graph = probability_graph)
    return dice_outcome

def get_dice_roll(dice_str: str) -> DiceOutcome:
    dice_to_roll: DiceToRoll = parse_dice_str(dice_str)
    outcome: DiceOutcome = decide_outcome_of_dice(dice_to_roll)
    return outcome
