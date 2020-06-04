class AbsolutePathIncluded(Exception):
    def __init__(self):
        super().__init__('Absolute path cannot be included.')


class IncludedDuplicate(Exception):
    def __init__(self, at: str):
        super().__init__(f'Site cannot include duplicates. '
                         f'Content at "{at}" already present.')


class InvalidCommand(Exception):
    """An invalid CLI command."""


class InvalidSiteCliUsage(Exception):
    pass