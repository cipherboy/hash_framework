from benchmarks.core import run_benchmarks

benchmarks = [
    {
        'name': 'associativity',
        'args': {
            'adder_cfg': [{"chaining": None, "type": "cla"}],
            'bits': 32,
        },
        'count': 2,
    },
    {
        'name': 'associativity',
        'args': {
            'adder_cfg': [{"chaining": None, "type": "rca"}],
            'bits': 32,
        },
        'count': 2,
    },
    {
        'name': 'associativity',
        'args': {
            'adder_cfg': [{"chaining": None, "type": "cla", "width": 8}, {"chaining": "rca", "type": "cla", "width": 8}, {"chaining": "rca", "type": "cla", "width": 8}, {"chaining": "rca", "type": "cla", "width": 8}],
            'bits': 32,
        },
        'count': 2,
    },
    {
        'name': 'associativity',
        'args': {
            'adder_cfg': [{"chaining": None, "type": "cla", "width": 8}, {"chaining": "csa", "type": "cla", "width": 8}, {"chaining": "csa", "type": "cla", "width": 8}, {"chaining": "csa", "type": "cla", "width": 8}],
            'bits': 32,
        },
        'count': 2,
    },
    {
        'name': 'associativity',
        'args': {
            'adder_cfg': [{"chaining": None, "type": "rca", "width": 8}, {"chaining": "rca", "type": "cla", "width": 8}, {"chaining": "rca", "type": "cla", "width": 8}, {"chaining": "rca", "type": "cla", "width": 8}],
            'bits': 32,
        },
        'count': 2,
    },
    {
        'name': 'associativity',
        'args': {
            'adder_cfg': [{"chaining": None, "type": "rca", "width": 8}, {"chaining": "csa", "type": "cla", "width": 8}, {"chaining": "csa", "type": "cla", "width": 8}, {"chaining": "csa", "type": "cla", "width": 8}],
            'bits': 32,
        },
        'count': 2,
    },
    {
        'name': 'associativity',
        'args': {
            'adder_cfg': [{"chaining": None, "type": "rca", "width": 8}, {"chaining": "rca", "type": "rca", "width": 8}, {"chaining": "rca", "type": "rca", "width": 8}, {"chaining": "rca", "type": "rca", "width": 8}],
            'bits': 32,
        },
        'count': 2,
    },
    {
        'name': 'associativity',
        'args': {
            'adder_cfg': [{"chaining": None, "type": "rca", "width": 8}, {"chaining": "csa", "type": "rca", "width": 8}, {"chaining": "csa", "type": "rca", "width": 8}, {"chaining": "csa", "type": "rca", "width": 8}],
            'bits': 32,
        },
        'count': 2,
    }
]

def __main__():
    s = run_benchmarks(benchmarks)
    print("=====STATISTICS=====")
    for i in range(0, len(s)):
        all_times = []
        for e in s[i]:
            all_times.append(e['time'])
        print("j: " + str(i) + " min: " + str(min(all_times)) + " max: " + str(max(all_times)) + " avg: " + str(sum(all_times) / len(all_times)))
    print("\n\n")
    print("=====RAW STATS=====")
    print(s)


if __name__ == "__main__":
    __main__()
