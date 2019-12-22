class NoSourcePath(Exception):
    def __init__(self):
        super().__init__('Content does not contain a valid `path`')


class AbsolutePathIncluded(Exception):
    def __init__(self):
        super().__init__('Absolute path cannot be included.')
