import multiprocessing
import time


def block_until_slots(queue, max_threads, granularity):
    while all(map(lambda x: not x.ready(), queue)) and len(queue) >= max_threads:
        time.sleep(granularity)

    new_results = []
    for proc in queue:
        if proc.ready():
            new_results.append(proc.get())

    return list(filter(lambda x: not x.ready(), queue)), new_results


def parallel_run(
    func, generator, processes=multiprocessing.cpu_count(), granularity=0.1, items_to_process=None
):
    pool = multiprocessing.Pool(processes)
    proc_queue: list = []
    results = []

    if callable(generator):
        generator = generator()

    processed = 0

    for item in generator:
        proc_queue, new_results = block_until_slots(proc_queue, processes, granularity)
        results.extend(new_results)
        new_proc = pool.apply_async(func, args=item, error_callback=print)
        proc_queue.append(new_proc)
        processed += 1
        if processed == items_to_process and items_to_process is not None:
            break

    pool.close()
    pool.join()

    for proc in proc_queue:
        if proc.ready():
            results.append(proc.get())

    return results
