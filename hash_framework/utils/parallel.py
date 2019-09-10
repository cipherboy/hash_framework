import multiprocessing
import time


def block_until_slots(queue, max_threads, granularity):
    while all(map(lambda x: not x.ready(), queue)) and len(queue) >= max_threads:
        time.sleep(granularity)

    return list(filter(lambda x: not x.ready(), queue))


def parallel_run(
    func, generator, processes=multiprocessing.cpu_count(), granularity=0.1
):
    pool = multiprocessing.Pool(processes)
    proc_queue: list = []

    for item in generator():
        proc_queue = block_until_slots(proc_queue, processes, granularity)
        new_proc = pool.apply_async(func, args=item, error_callback=print)
        proc_queue.append(new_proc)

    pool.close()
    pool.join()
    return None
