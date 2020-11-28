# god this is so stupid

registered_stids = {}


def for_all_methods(decorator):
    exclude = ["method", "bar"]

    def decorate(cls):
        for attr in cls.__dict__:  # there's probably a better way to do this
            # print(attr, type(getattr(cls, attr)))
            if callable(getattr(cls, attr)) and attr not in exclude:
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate


def register():
    def decorate(cls):
        assert isinstance(cls, type)
        registered_stids[str(cls.__name__)] = cls
        return cls

    return decorate


from types import SimpleNamespace


class stid1(SimpleNamespace):

    def slid1(var: str):
        print("slid1", var)


class stid2:

    def slid1(args):
        print("This slid2! Args:", args)


def method(cls):
    print("hello")
    for k, v in cls.__dict__.items():
        print(k, type(v))


for v in list(globals().values()):
    if isinstance(v, type) and v.__name__.startswith("stid"):
        for_all_methods(staticmethod)(register()(v))
        setattr(v, "method", classmethod(method))

# stmt = stid1.slid1("var here")

# from timeit import timeit

# print(timeit(lambda: stmt))

# stid1().method()

print("Regs:", registered_stids)

getattr(registered_stids["stid1"], "slid1")("args")
stid1.slid1("args")

x = registered_stids["stid1"]
assert isinstance(x, type)
