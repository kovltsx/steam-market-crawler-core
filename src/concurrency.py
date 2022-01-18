from threading import Thread, Lock
from queue import Queue

lock = Lock()

class Worker(Thread):
    """ Thread that execute tasks given a Queue
    """
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:

            try:
                func, args, kargs = self.tasks.get()
            except:
                break

            try:
                func(*args, **kargs)
            except Exception as e:
                print(e)

            self.tasks.task_done()


class ThreadPool:
    """ Pool of threads that execute given callables
    """
    def __init__(self, num_threads):
        """ Initialize queues given a number of threads
        """
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue
        """
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue
        """
        self.tasks.join()
