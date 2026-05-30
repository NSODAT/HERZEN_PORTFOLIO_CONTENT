import logging
from ExceptionClass import *

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


def tree_to_dict(node):
    if node is None:
        return None
    return {
        'value': node.value,
        'left': tree_to_dict(node.left),
        'right': tree_to_dict(node.right)
    }


def gen_bin_tree_rec(height=4, root=8):
    try:
        if height < 0:
            raise InvalidHeightError("Высота дерева не может быть отрицательной.")
        if root < 0:
            raise InvalidRootError("Корень дерева не может быть отрицательным.")

        if height == 0:
            return None

        root_node = TreeNode(root)
        if height > 1:
            root_node.left = gen_bin_tree_rec(height - 1, root + root // 2)
            root_node.right = gen_bin_tree_rec(height - 1, root ** 2)
            gen_bin_tree_logger.info(f"Узел с данными {root} построен.")
    except InvalidHeightError as e:
        # Логирование ошибки
        gen_bin_tree_logger.error(f"Ошибка при построении левого поддерева: {e}")
    except InvalidRootError as e:
        # Логирование ошибки
        gen_bin_tree_logger.error(f"Ошибка при построении правого поддерева: {e}")

    return root_node


def gen_bin_tree_norec(height=4, root=8):
    try:
        if height < 0:
            raise InvalidHeightError("Высота дерева не может быть отрицательной.")
        if root < 0:
            raise InvalidRootError("Корень дерева не может быть отрицательным.")
        if height == 0:
            return None

        root_node = TreeNode(root)
        stack = [root_node]
        for i in range(1, height):
            current = []
            for node in stack:
                if node is not None:
                    left_value = node.value + node.value // 2
                    right_value = node.value ** 2

                    node.left = TreeNode(left_value)
                    node.right = TreeNode(right_value)

                    current.append(node.left)
                    current.append(node.right)
                    gen_bin_tree_logger.info(f"Узел с данными {root} построен.")
                else:
                    current.append(None)
                    current.append(None)

            stack = current
        return tree_to_dict(root_node)
    except InvalidHeightError as e:
        # Логирование ошибки
        gen_bin_tree_logger.error(f"Ошибка при построении левого поддерева: {e}")
    except InvalidRootError as e:
        # Логирование ошибки
        gen_bin_tree_logger.error(f"Ошибка при построении правого поддерева: {e}")


def main():
    try:
        method = int(input("Выберите метод построения бинарного дерева(1 - рекурсивный, 2 - нерекурсивный:\n"))
        height = int(input("Введите высоту бинарного дерева:\n"))
        if height < 0:
            raise InvalidHeightError("Высота дерева не может быть отрицательной.")
        root = float(input("Введите корневое значение бинарного дерева: \n"))
        if root < 0:
            raise InvalidRootError("Корень дерева не может быть отрицательным.")
        match method:
            case 1:
                tree = gen_bin_tree_rec(height, root)
                tree_dict = tree_to_dict(tree)
                main_logger.info("Дерево сгенерировано успешно.")
                print(tree_dict)
            case 2:
                main_logger.info("Дерево сгенерировано успешно.")
                print(gen_bin_tree_norec(height, root))
    except InvalidHeightError as e:
        # Логирование ошибки
        main_logger.error(f"Ошибка при вводе высоты: {e}")
    except InvalidRootError as e:
        # Логирование ошибки
        main_logger.error(f"Ошибка при вводе корня: {e}")

main_logger = logging.getLogger('main')
main_logger.setLevel(logging.DEBUG)


main_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
main_handler = logging.StreamHandler()
main_handler.setFormatter(logging.Formatter(main_format))
main_logger.addHandler(main_handler)


gen_bin_tree_logger = logging.getLogger('gen_bin_tree')
gen_bin_tree_logger.setLevel(logging.DEBUG)


gen_bin_tree_format = '%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s'
gen_bin_tree_handler = logging.StreamHandler()
gen_bin_tree_handler.setFormatter(logging.Formatter(gen_bin_tree_format))
gen_bin_tree_logger.addHandler(gen_bin_tree_handler)

if __name__ == '__main__':
    main()
