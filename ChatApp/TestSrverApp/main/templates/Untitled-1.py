import time
x = str(input('\033[32mЧей акаунт хотите взломать:'))
print()
print(f'\033[342mВзлом акаунта {x}')
def progress_bar(total, current):
    progress = current / total
    bar_length = 40
    filled_length = int(progress * bar_length)
    bar = '█' * filled_length + '.' * (bar_length - filled_length)
    percentage = int(progress * 100)
    print(f'{bar} {percentage}%')
for i in range(10):
    time.sleep(0.5)
    progress_bar(10, i+1)
print("Процес взломапрошол удачно!!!")