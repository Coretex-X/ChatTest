'''x = str(input('Ведите текст любой длины:'))
list1 = []
for i, x in enumerate(x):
    z = ord(x)
    list1.append(str(z))

print()
print(".".join(list1))'''

import random
print('Что вы выбирите:\n1.Защифровать\n2.Расщифровать')
print()
x = str(input(':'))

def encrypt():
    text = input("Введите текст: ")
    key = 42  # Секретный ключ
    separators = [".", "-", "|", "_", "*"]  # Случайные разделители
    encoded_parts = []
    for char in text:
        encoded_char = ord(char) ^ key  # XOR-шифрование
        separator = random.choice(separators)
        encoded_parts.append(f"{encoded_char}{separator}")
    encoded = "".join(encoded_parts)[:-1]  # Убираем последний разделитель
    print()
    print(encoded)

if x == 1:
    encrypt()
elif x == 2:
    pass
