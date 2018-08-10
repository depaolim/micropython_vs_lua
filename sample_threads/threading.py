import _thread

get_ident = _thread.get_ident


class Thread:

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None):
        self.target = target
        self.args = args
        self.kwargs = {} if kwargs is None else kwargs

    def start(self):
        self.running = _thread.allocate_lock()
        self.running.acquire()
        _thread.start_new_thread(self.run, ())

    def join(self):
        assert self.running.acquire()

    def run(self):
        self.target(*self.args, **self.kwargs)
        self.running.release()
