import cmsh

def prefix_keys(d, prefix):
    assert(type(d) == dict)
    assert(type(prefix) == str)
    r = {}
    for k in d:
        r[prefix + str(k)] = d[k]
    return r

def unprefix_keys(d, prefix):
    assert(type(d) == dict)
    assert(type(prefix) == str)
    r = {}
    for k in d:
        if k[0:len(prefix)] == prefix:
            r[k[len(prefix):]] = d[k]
    return r

def print_dict(d, n):
    assert(type(d) == dict)
    assert(type(n) == str)
    print("===begin " + n + "===")
    for k in d:
        print("\t" + str(k) + ": " + str(d[k]))
    print("===end " + n + "===")

def merge_dict(ds):
    assert(type(ds) == list)
    assert(len(ds) > 0)
    assert(type(ds[0]) == dict)
    r = {}
    for d in ds:
        for k in d:
            assert(not k in r)
            r[k] = d[k]
    return r

def print_cmsh(obj):
    print(repr_cmsh(obj))

def repr_cmsh(obj):
    if isinstance(obj, (list, tuple)):
        return "[" + ", ".join([repr_cmsh(part) for part in obj]) + "]"
    elif isinstance(obj, cmsh.Vector):
        return str(int(obj))
    elif isinstance(obj, cmsh.Variable):
        if obj.model.sat:
            return str(bool(obj))
        else:
            return "v" + int(obj)
    else:
        return str(obj)
