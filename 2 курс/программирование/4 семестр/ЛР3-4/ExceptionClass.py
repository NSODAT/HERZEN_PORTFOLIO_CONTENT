class BinaryTreeError(Exception):
    """Базовый класс для исключений, связанных с бинарными деревьями."""
    pass

class InvalidHeightError(BinaryTreeError):
    """Ошибка, возникающая при некорректной высоте дерева."""
    pass

class InvalidRootError(BinaryTreeError):
    """Ошибка, возникающая при некорректном корне дерева."""
    pass