from jobh import JobManager, JobStruct
from threading import Thread

YA_BOY_VARIABLE = 0

def increment_var():
    global YA_BOY_VARIABLE
    YA_BOY_VARIABLE += 1
    print("my var is %s" % YA_BOY_VARIABLE)


if __name__ == "__main__":
    jm = JobManager()
    jm.start()

    threads = []
    jobs = []
    for _ in range(100):
        job = JobStruct(jm, increment_var)
        jobs.append(job)
        t = Thread(target=jm.add_job(job))
        t.start()
        threads.append(t)

    for j in jobs:
        jm.get_job_results(j.job_id)

    for t in threads:
        t.join()

    print("done. var is: %s" % YA_BOY_VARIABLE)
    jm.kill()
    