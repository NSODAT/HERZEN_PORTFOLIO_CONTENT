import random

def generate_data(num_tests):
    data = []
    for i in range(num_tests):
        height = random.randint(1, 10)
        root = random.randint(1, 100)
        data.append((height, root))
    return data