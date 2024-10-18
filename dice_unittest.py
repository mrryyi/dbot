import unittest
from dice import *

class TestDiceFunctions(unittest.TestCase):
    def test_is_valid_dice_str(self):
        self.assertTrue(is_valid_dice_str('1d6'))
        self.assertTrue(is_valid_dice_str('10d10'))
        self.assertTrue(is_valid_dice_str('100d100'))
        self.assertFalse(is_valid_dice_str('d6'))
        self.assertFalse(is_valid_dice_str('1d'))
        self.assertFalse(is_valid_dice_str('1d6d6'))
        self.assertFalse(is_valid_dice_str('1d6d'))
        self.assertFalse(is_valid_dice_str('1d6d6d6'))
    
    def test_decide_outcome_of_dice(self):
        dice: DiceToRoll = DiceToRoll(amount_of_dice=3, dice_value=6)

        def mock_rng(a: int, b: int) -> int:
            return 2
        
        outcome: DiceOutcome = decide_outcome_of_dice(dice, mock_rng)
        self.assertEqual(outcome.outcome, 6) # 2 + 2 + 2 = 6
    
    def test_prepare_probability_data(self):
        distribution: dict[int, float] = {1: 0.5, 2: 0.5}
        data = prepare_probability_data(distribution, result=1)
        self.assertEqual(data['keys'], [1, 2])
        self.assertEqual(data['values'], [0.5, 0.5])
        self.assertEqual(data['highlight'], 1)
    
    def test_dice_probability_distribution(self):
        dice: DiceToRoll = DiceToRoll(amount_of_dice=2, dice_value=6)
        distribution = dice_probability_distribution(dice)
        # Floating point precision is the paragon of consistency.
        self.assertEqual(distribution, {2: 1/36, 3: 2/36, 4: 3/36, 5: 4/36, 6: 5/36, 7: 6/36, 8: 5/36, 9: 4/36, 10: 3/36, 11: 2/36, 12: 1/36})

if __name__ == '__main__':
    unittest.main()