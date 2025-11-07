import random
import re

def roll_dice(dice_str: str) -> int:
    dice_str = dice_str.replace(" ", "")
    pattern = r"([+-]?\d*d\d+|[+-]?\d+)"
    tokens = re.findall(pattern, dice_str)

    total = 0
    for token in tokens:
        if "d" in token:
            sign = -1 if token.startswith("-") else 1
            token = token.lstrip("+-")
            num, die = token.split("d")
            num = int(num) if num else 1 
            die = int(die)
            subtotal = sum(random.randint(1, die) for _ in range(num))
            total += sign * subtotal
        else:
            total += int(token)
    return total
