class Benchmark:
    def __init__(self, args):
        # Initialize benchmark object; accepts dict of arguments
        pass

    def setup(self):
        # Sets up shared information for all benchmarks; is called once
        # before self.run()
        pass

    def run(self, count, max_time):
        # Runs each benchmark <count> times, stopping when the difficulty
        # of the benchmark exceeds <max_time>.
        pass

    def timings(self):
        # Returns an array of timings + identifiers + additional information
        # for all benchmarks ran.
        pass

    def clean(self):
        # Cleans up after benchmark.
        pass
