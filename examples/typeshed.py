from typing import List

def my_function(numbers: List[int]) -> int:
    """Это функция принимает список чисел и возвращает сумму"""
    total = 0
    for number in numbers:
        total += number
    return total

# Example
numbers = [1, 2, 3]
result = my_function(numbers)
print(result)
