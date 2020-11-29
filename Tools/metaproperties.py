# I don't entirely see the need for the _is_dirty attribute, that can probably be gotten rid of

from typing import Union

__all__ = ('self_properties', 'properties')


def self_properties(self, scope: dict, exclude=(), save_args: bool = False):
    """Copies all items from `scope` to self as attributes with single underscore prefix.
    :param self: instance ref.
    :param scope: dictionary with attributes.
    :param exclude: tuple with names to exclude from `scope`.
    :param save_args: if True, sets self._args with a tuple with `(scope - exclude).values`
    """
    if save_args:
        args = []
        for (k, v) in scope.items():
            if k != 'self' and k not in exclude:
                setattr(self, '_' + k, v)
                args.append(v)
        self._args = tuple(args)
    else:
        for (k, v) in scope.items():
            if k != 'self' and k not in exclude:
                setattr(self, '_' + k, v)


class properties:
    """
    Utilities for building properties with extended features.
    """

    __slots__ = ['_slots', '_scope', '_var', '_auto_dirty']

    def __init__(self, scope: dict, var_name: str, auto_dirty: bool = False):
        self._slots = []
        self._scope = scope
        self._var = var_name
        self._auto_dirty = auto_dirty

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        # Export slots to scope
        slots = self._scope.get('__slots__', None)
        if slots is None:
            self._scope['__slots__'] = tuple(self._slots)
        elif isinstance(slots, list):
            self._scope['__slots__'] += self._slots
        elif isinstance(slots, tuple):
            self._scope['__slots__'] = (*self._scope['__slots__'], *self._slots)

        # Clean scope
        if self._var in self._scope:
            del self._scope[self._var]

        # Clean references
        self._scope = None
        self._slots = None
        self._var = None

    def prop(self, read_only: bool = False, listener: Union[bool, str] = None, auto_dirty=False):
        """Decorator: Generates a property with additional features.
        :param read_only: if True, only a getter is generated.
        :param listener: if str, changes will fire `self.[listener]`, if bool, changes will fire `self._changed`
        :param auto_dirty: if True, changes will set `self._is_dirty`
        :return: property.
        """

        auto_dirty = self._auto_dirty or auto_dirty

        if auto_dirty and '_is_dirty' not in self._slots:
            self._slots.append('_is_dirty')

        def decorator(f):

            field = '_' + f.__name__

            if read_only and listener:
                raise ValueError(f"property {field} cannot be read_only and observable at the same time.")

            self._slots.append(field)

            if read_only:
                setter = None
            else:
                if listener:
                    listener_name = listener if isinstance(listener, str) else '_changed'

                    def setter(inst, new):
                        old = getattr(inst, field, None)
                        if old != new:
                            setattr(inst, field, new)
                            if auto_dirty:
                                inst._is_dirty = True
                            (getattr(inst, listener_name))(field, old, new)
                else:
                    def setter(inst, new):
                        if getattr(inst, field, None) != new:
                            setattr(inst, field, new)
                            if auto_dirty:
                                inst._is_dirty = True

            return property(
                lambda inst: getattr(inst, field, f(inst)),
                setter,
                None,
                f.__doc__
            )

        return decorator


##class Foo:
##    with properties(locals(), 'meta') as meta:
##
##        @meta.prop(read_only = True)
##        def name(self) -> str:
##            '''Name'''
##            return self.__class__
##
##        @meta.prop(listener="val_change")
##        def var(self):
##            '''var'''
##            return None
##    
##    def __init__(self, var):
##        self_properties(self, locals())
##        print("Dir:", dir(self))
##
##    def var_change(self, prop, old, new):
##        print("Old value was", old)
##        print("New value is", new)
##
##f = Foo("I'm a variable")
