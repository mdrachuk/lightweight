from lightweight.empty import empty, Empty


def test_equals():
    empty1 = Empty()
    return empty == empty1


def test_is():
    empty2 = Empty()
    return empty is empty2


def test_instance():
    return isinstance(empty, Empty)


def test_repr():
    return str(empty) == '<lightweight.empty>'
