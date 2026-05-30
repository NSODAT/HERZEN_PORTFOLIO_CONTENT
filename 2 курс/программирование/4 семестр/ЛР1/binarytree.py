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
    if height == 0:
        return None

    root_node = TreeNode(root)
    if height > 1:
        root_node.left = gen_bin_tree_rec(height - 1, root + root // 2)
        root_node.right = gen_bin_tree_rec(height - 1, root ** 2)

    return root_node


def gen_bin_tree_norec(height=4, root=8):
    if height < 0:
        return None
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
            else:
                current.append(None)
                current.append(None)

        stack = current
    return tree_to_dict(root_node)


def main():
    method = int(input("Выберите метод построения бинарного дерева(1 - рекурсивный, 2 - нерекурсивный:\n"))
    height = int(input("Введите высоту бинарного дерева:\n"))
    root = float(input("Введите корневое значение бинарного дерева: \n"))
    match method:
        case 1:
            tree = gen_bin_tree_rec(height, root)
            tree_dict = tree_to_dict(tree)
            print(tree_dict)
        case 2:
            print(gen_bin_tree_norec(height, root))


if __name__ == '__main__':
    main()
