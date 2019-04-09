from threading import Thread, Lock
import queue
import time

class JobManager(Thread):
    """create one thread of this"""
    def __init__(self):
        self.results = dict()  # key being the job_id
        self.dead = False

        # "private" variables
        self.__killsig = False
        self.__cur_job_id = 0
        self.__jobs = queue.Queue()
        Thread.__init__(self)

    def kill(self):
        self.__killsig = True

    def get_next_job_id(self):
        """only jobstruct should call this"""
        lock = Lock()
        lock.acquire()
        self.__cur_job_id += 1
        result = self.__cur_job_id
        lock.release()
        return result

    def add_job(self, job):
        assert isinstance(job, JobStruct)
        self.__jobs.put_nowait(job)

    def get_job_results(self, job_id):
        """behaves like join(). uses a wait loop so that it is responsive to kill() commands"""
        while not self.__killsig:
            if job_id in self.results:
                return self.results.pop(job_id, None)
            time.sleep(0.5)

    def run(self):
        """thread run method override"""
        while not self.__killsig:
            if self.__jobs.qsize() == 0:
                time.sleep(0.1)
                continue
            job = self.__jobs.get_nowait()
            output = job.func(*job.args, **job.kwargs)

            # prevent clutter of the output dictionary if no one cares about the result
            if job.output_matters:
                self.results[job.job_id] = output
        self.dead = True


class JobStruct:
    """description of what the jobmanager should run."""
    def __init__(self, jobmanager, func, args=list(), kwargs=dict(), output_matters=True):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.job_id = jobmanager.get_next_job_id()
        self.output_matters = output_matters