"""
Base plugin class with registration mechanism and configuration reading.
"""
import abc


def _resolve_name(name):
    """Resolves the name and returns the corresponding object."""
    ret = None
    parts = name.split('.')
    cursor = len(parts)
    module_name = parts[:cursor]
    last_exc = None

    while cursor > 0:
        try:
            ret = __import__('.'.join(module_name))
            break
        except ImportError, exc:
            last_exc = exc
            if cursor == 0:
                raise
            cursor -= 1
            module_name = parts[:cursor]

    for part in parts[1:]:
        try:
            ret = getattr(ret, part)
        except AttributeError:
            if last_exc is not None:
                raise last_exc
            raise ImportError(name)

    if ret is None:
        if last_exc is not None:
            raise last_exc
        raise ImportError(name)

    return ret


class PluginRegistry(object):
    """Abstract Base Class for plugins."""
    __metaclass__ = abc.ABCMeta

    @classmethod
    def _get_backend_class(cls, name):
        try:
            klass = _resolve_name(name)
        except ImportError:
            msg = ('Unknown fully qualified name for the backend: %r') % name
            raise KeyError(msg)

        # let's register it
        cls.register(klass)
        return klass

    @classmethod
    def get(cls, name, *args, **kw):
        """Instanciates a plugin given its fully qualified name."""
        klass = cls._get_backend_class(name)
        return klass(*args, **kw)

    @classmethod
    def __subclasshook__(cls, klass):
        for method in cls.__abstractmethods__:
            if any(method in base.__dict__ for base in klass.__mro__):
                continue
            raise TypeError('Missing "%s" in "%s"' % (method, klass))
        if klass not in cls._abc_registry:
            cls._abc_registry.add(klass)
        return True
