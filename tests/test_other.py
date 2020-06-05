from jinja2.utils import LRUCache

from lightweight.templates import LruCachePerCwd


def test_package():
    pass


def test_per_cwd_jinja_cache_creation():
    cache = LruCachePerCwd(100)
    jlru = cache.instance()
    assert isinstance(jlru, LRUCache)
    assert jlru.capacity == 100


class CallRecorder:
    def __getattr__(self, name):
        self.last_access = name
        return self.save_params

    def save_params(self, *args, **kwargs):
        self.la_args = args
        self.la_kwargs = kwargs

    def __repr__(self):
        self.last_access = '__repr__'
        self.la_args = []
        self.la_kwargs = {}


class MockCache(LruCachePerCwd):
    def __init__(self, recorder: CallRecorder):
        super().__init__(100)
        self.recorder = recorder

    def instance(self):
        return self.recorder


def test_per_cwd_jinja_cache_calls():
    cr = CallRecorder()
    cache = MockCache(cr)
    cache.__getstate__(1, a='a', b='b')
    assert cr.last_access == '__getstate__'

    cache.__setstate__(1, a='a', b='b')
    assert cr.last_access == '__setstate__'

    cache.__getnewargs__(1, a='a', b='b')
    assert cr.last_access == '__getnewargs__'

    cache.copy(1, a='a', b='b')
    assert cr.last_access == 'copy'

    cache.get(1, a='a', b='b')
    assert cr.last_access == 'get'

    cache.setdefault(1, a='a', b='b')
    assert cr.last_access == 'setdefault'

    cache.clear(1, a='a', b='b')
    assert cr.last_access == 'clear'

    cache.__contains__(1, a='a', b='b')
    assert cr.last_access == '__contains__'

    cache.__len__(1, a='a', b='b')
    assert cr.last_access == '__len__'

    cache.__repr__()
    assert cr.last_access == '__repr__'

    cache.__getitem__(1, a='a', b='b')
    assert cr.last_access == '__getitem__'

    cache.__setitem__(1, a='a', b='b')
    assert cr.last_access == '__setitem__'

    cache.__delitem__(1, a='a', b='b')
    assert cr.last_access == '__delitem__'

    cache.items(1, a='a', b='b')
    assert cr.last_access == 'items'

    cache.iteritems(1, a='a', b='b')
    assert cr.last_access == 'iteritems'

    cache.values(1, a='a', b='b')
    assert cr.last_access == 'values'

    cache.itervalue(1, a='a', b='b')
    assert cr.last_access == 'itervalue'

    cache.keys(1, a='a', b='b')
    assert cr.last_access == 'keys'

    cache.iterkeys(1, a='a', b='b')
    assert cr.last_access == 'iterkeys'

    cache.__reversed__(1, a='a', b='b')
    assert cr.last_access == '__reversed__'

    cache.__iter__(1, a='a', b='b')
    assert cr.last_access == '__iter__'

    cache.__copy__(1, a='a', b='b')
    assert cr.last_access == '__copy__'
