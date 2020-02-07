
class JobFailed(RuntimeError):
    def __init__(self, job ):
        self.job = job
        msg = job.err.split("\n")[-1]
        super().__init__(msg)
