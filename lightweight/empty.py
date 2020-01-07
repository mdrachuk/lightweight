class _SingletonMeta(type):
    _instance = None

    def __call__(self):
        if self._instance is None:
            self._instance = super().__call__()
        return self._instance


class Empty(metaclass=_SingletonMeta):
    """An alternative to None, when None is a legitimate option for a function argument,
    but it also such an argument can be omitted. See [Site.copy(...)][lightweight.site.copy]

    Empty is a singleton.
    """

    def __eq__(self, other):
        return isinstance(other, Empty)


empty = Empty()
