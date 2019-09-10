import cmsh


def print_cmsh(obj):
    print(repr_cmsh(obj))


def repr_cmsh(obj) -> str:
    if isinstance(obj, (list, tuple)):
        return "[" + ", ".join([repr_cmsh(part) for part in obj]) + "]"
    if isinstance(obj, cmsh.Vector):
        return str(int(obj))
    if isinstance(obj, cmsh.Variable):
        if obj.model.sat:
            return str(bool(obj))
        return "v" + int(obj)
    return str(obj)
