class Enum:
    """
    Object supporting CircuitPython-style of static symbols
    as seen with Direction.OUTPUT, Pull.UP
    """

    def __repr__(self):
        """
        Assumes instance will be found as attribute of own class.
        Returns dot-subscripted path to instance
        (assuming absolute import of containing package)
        """
        cls = type(self)
        for key in dir(cls):
            if getattr(cls, key) is self:
                return f"{cls.__module__}.{cls.__qualname__}.{key}"
        return repr(self)

    def __str__(self):
        cls = type(self)
        for key in dir(cls):
            if getattr(cls, key) is self:
                return f"{key}"

        return repr(self)

    @classmethod
    def iteritems(cls):
        """
        Inspects attributes of the class for instances of the class
        and returns as key,value pairs mirroring dict#iteritems
        """
        for key in dir(cls):
            val = getattr(cls, key)
            if isinstance(cls, val):
                yield (key, val)
