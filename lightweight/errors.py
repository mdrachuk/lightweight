class NoSourcePath(Exception):
    def __init__(self):
        super().__init__('Content does not contain a valid `path`')


class AbsolutePathIncluded(Exception):
    def __init__(self):
        super().__init__('Absolute path cannot be included.')


class IncludedDuplicate(Exception):
    def __init__(self):
        super().__init__('Site cannot include duplicates.')


class MissingSiteUrl(Exception):
    def __init__(self):
        super().__init__('Site().url property is not set.')
