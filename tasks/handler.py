import multiprocessing

from tasks.worker import Worker


def exec_tasks(tasks, n_workers=None, **kwargs):
    results = []

    tasks_queue = multiprocessing.Queue()
    results_queue = multiprocessing.Queue()

    if n_workers is None:
        n_workers = multiprocessing.cpu_count() * 4

    print('Creating %d workers' % n_workers)
    workers = [Worker(tasks_queue, results_queue, requests_handler=True, **kwargs) for _ in range(n_workers)]
    n_tasks = 0

    for w in workers:
        w.start()
    try:
        for task in tasks:
            tasks_queue.put(task)
            n_tasks += 1

        for w in range(n_workers):
            tasks_queue.put(None)

        for res in range(n_tasks):
            result = results_queue.get()
            if result is not None:
                results.append(result)

        print('Joining...')
        for w in workers:
            w.join()

    except KeyboardInterrupt:
        for w in workers:
            w.terminate()
        os._exit(1)
    except Exception as e:
        print(e)
        raise e
    finally:
        return results
