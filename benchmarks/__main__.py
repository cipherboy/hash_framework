from benchmarks.core import run_benchmarks

def __main__():
    benchmarks = []
    test = "equality"
    base_adders = ["rca", "cla"]
    chainings = ["rca", "csa"]
    shapes = ["left", "right", "tree"]
    bits = 8
    count = 1
    for w in [256, 128, 64, 32, 16, 8, 4, 2]:
        if w > bits:
            continue

        segments = bits//w
        print(segments)
        for chaining in chainings:
            for base_adder in base_adders:
                for shape in shapes:
                    o = {}
                    o['name'] = test
                    o['count'] = count
                    o['args'] = {}
                    o['args']['bits'] = bits
                    o['args']['shape'] = shape
                    ac = [{'chaining': None, "type": base_adder, "width": w}]
                    while len(ac) < segments:
                        ac.append({'chaining': chaining, 'type': base_adder, 'width': w})
                    o['args']['adder_cfg'] = ac
                    benchmarks.append(o)

    print("Benchmarks: " + str(len(benchmarks)))

    # assert(False)


    s = run_benchmarks(benchmarks)
    print("=====CONFIG=====")
    print(benchmarks)
    print("\n\n")
    print("=====RAW STATS=====")
    print(s)
    print("\n\n")
    print("=====STATISTICS=====")
    for i in range(0, len(s)):
        all_times = []
        for e in s[i]:
            all_times.append(e['time'])
        print("j: " + str(i) + " min: " + str(min(all_times)) + " max: " + str(max(all_times)) + " avg: " + str(sum(all_times) / len(all_times)))
    print("\n\n")

if __name__ == "__main__":
    __main__()
