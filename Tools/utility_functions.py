from types import *
from typing import *


def remove_prefix(text: str, prefixes: Iterable) -> str:
    for prefix in prefixes:
        if text.startswith(prefix):
            return text[len(prefix):]
    return text  # or whatever


def remove_suffix(text: str, suffixes: Iterable) -> str:
    for suffix in suffixes:
        if text.endswith(suffix):
            return text[:-len(suffix)]
    return text  # or whatever


def dict_kv(dictionary: dict) -> list:
    return list(dictionary.keys()) + list(dictionary.values())


def invert_dict(dictionary: dict) -> dict:
    return {v: k for k, v in dictionary.items()}


def recursive_join(separator, *args) -> str:
    return str(separator).join([recursive_join(separator, *x) if type(x) is list else str(x) for x in args])


def flatten(input_list):
    if not input_list:
        return input_list
    if isinstance(input_list[0], list):
        return flatten(input_list[0]) + flatten(input_list[1:])
    return input_list[:1] + flatten(input_list[1:])


def list_duplicates(seq):
    seen = set()
    seen_add = seen.add
    # adds all elements it doesn't know yet to seen and all other to seen_twice
    seen_twice = set(x for x in seq if x in seen or seen_add(x))
    return seen_twice


def call_with(func: 'function', arg_dict: 'dict', type_checking=False):
    """
    Calls function 'func' and supplies necessary arguments from dictionary 'arg_dict'. Works with both
    positional and keyword arguments. Function output is returned so that it may be used elsewhere.
    If 'type_checking' is set to True, function arguments will be type-checked according to the function's
    __annotations__ dictionary (if an argument does not have a type annotation it will be skipped).

    :arg func: function to be run
    :arg arg_dict: dictionary of arguments with which func is to be ran (keys in dictionary must match
                   argument names in function)
    :arg type_checking: boolean for whether arguments should be type-checked
    """

    function_variables = func.__code__.co_varnames

    if type_checking:
        annotations = func.__annotations__

    args = []

    for var in function_variables:
        try:
            # now I'm fairly certain that this ought to implement short-circuit behavior and not check the other
            # conditions if type_checking evaluates to False, but program behaviors always manage to surprise me,
            # so if that's not the case and it breaks, just add "annotations = []" above I guess.
            if type_checking and var in annotations and not isinstance(arg_dict[var], annotations[var]):

                try:
                    var = annotations[var](var)

                except ValueError:
                    raise TypeError("{0} is not of correct type {1}".format(var, annotations[var]))

            args.append(arg_dict[var])
        except KeyError as e:
            raise KeyError("Argument {0} not found in supplied dictionary".format(e))

    return func(*args)


class cache_decorator:
    # builds left (least recent) to right (most recent)

    # def __new__(cls, *args, **kwargs):
    #     print(cls, args, kwargs)
    #     # super(cache_decorator, cls)
    #     return super().__new__(cls)

    def __init__(self, size=50):
        from collections import OrderedDict

        self.size = size
        self.cache_dict = OrderedDict()

    def __call__(self, func):
        # print(self, func)

        def wrapper(*args, **kwargs):
            # print("\nUsing args:", args, kwargs)
            # print(self.cache_dict)

            # if a key is already in the dict, moves it to the front (right side) as the most recent
            if args in self.cache_dict:
                self.cache_dict.move_to_end(args)
                return self.cache_dict[args]

            else:
                val = func(*args, **kwargs)

                if len(self.cache_dict) >= self.size:
                    self.cache_dict.popitem(False)

                # inserts item at front (right side)
                self.cache_dict[args] = val

                return val

        return wrapper


def repeat(repeats: int, func: callable, *args):
    for _ in range(repeats):

        if not isinstance(args, Iterable) or isinstance(args, str):
            args = [args]

        args = func(*args)

    return args


def remove_redundancies(input_list: list):
    import copy
    list_copy = copy.deepcopy(input_list)

    if not list_copy:
        return list_copy

    # if not isinstance(L, Iterable):
    #     return L

    if isinstance(list_copy, list):
        if len(list_copy) == 1:
            list_copy = remove_redundancies(list_copy[0])
        else:
            for i in range(len(list_copy)):
                list_copy[i] = remove_redundancies(list_copy[i])

    return list_copy
