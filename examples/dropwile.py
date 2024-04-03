from itertools import dropwhile

numbers = [1, 2, 3, 0, 0, 4, 5]

# Отбросить все элементы, пока не встретится число, большее 0
result = dropwhile(lambda x: x <= 0, numbers)
print(list(result))
