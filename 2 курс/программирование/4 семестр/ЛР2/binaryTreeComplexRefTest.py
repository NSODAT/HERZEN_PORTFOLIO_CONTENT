import timeit
import matplotlib.pyplot as plt

from setup_data import generate_data

# Рекурсивный алгоритм
def gen_bin_tree_recursive(height, root):
    if height == 0:
        return {'data': root}

    return {
        'data': root,
        'left': gen_bin_tree_recursive(height - 1, root + root // 2),
        'right': gen_bin_tree_recursive(height - 1, root ** 2),
    }

# Нерекурсивный алгоритм
def gen_bin_tree_iterative(height, root):
    if height == 0:
        return {'data': root}

    tree = {'data': root}
    queue = [tree]

    for level in range(1, height):
        new_queue = []
        for node in queue:
            left_leaf = node['data'] + node['data'] // 2
            right_leaf = node['data'] ** 2
            node['left'] = {'data': left_leaf}
            node['right'] = {'data': right_leaf}
            new_queue.append(node['left'])
            new_queue.append(node['right'])
        queue = new_queue

    return tree

# Сравнение времени выполнения
num_iterations = 1000
num_tests = 100

data = generate_data(num_tests)

recursive_times = []
iterative_times = []

for height, root in data:
    recursive_time = timeit.timeit(
        lambda: gen_bin_tree_recursive(height, root),
        number=num_iterations
    )
    iterative_time = timeit.timeit(
        lambda: gen_bin_tree_iterative(height, root),
        number=num_iterations
    )
    recursive_times.append(recursive_time)
    iterative_times.append(iterative_time)

import matplotlib.pyplot as plt

# Создаем гистограмму
plt.hist(recursive_times, bins=20, label="Рекурсивный", alpha=0.5)  # Уменьшаем прозрачность
plt.hist(iterative_times, bins=20, label="Нерекурсивный", alpha=0.5)  # Уменьшаем прозрачность

# Настраиваем гистограмму
plt.xlabel("Время выполнения (сек)")
plt.ylabel("Количество значений")
plt.legend()
plt.grid()  # Добавляем сетку для лучшей читаемости

# Отображаем график
plt.show()