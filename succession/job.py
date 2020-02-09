import asyncio
import logging

logger= logging.getLogger(__name__)

async def nothing_to_do():
    return


class OutputSender:
    def __init__(self,job):
        self.job  = job

    def __enter__(self,):
        return self

    def __exit__(self, ev,et, tb):
        """Send any capture err, and out strings to the logging
        subsystem.
        """
        if ev is None:
            error = logger.error
        else:
            error = logger.critical

        if self.job.out:
            logger.info(self.job.out)
        if self.job.err:
            error(self.job.err,)


class Job:
    def __init__(self,):
        self.dependencies = set()
        self.done = False
        self.out = None
        self.err = None

    def add_dependency(self, newdep):
        """Adds another job as a add_dependency of this job.

        Dependencies are jobs whihc must be Ok() before 
        this job runs.

        :returns: self
        """
        self.dependencies.add(newdep)
        return self

    def Ok(self):
        """Return false if 'target' is not upto-date. Ie the Job needs to be run"""
        return ( self.check_self() and
                all( d.Ok() for d in self.dependencies ))

    def Run(self,):
        """Return completion promise for upto date ness of this job"""
        if not self.Ok():
            return self._run()
        else:
            return nothing_to_do()
    async def _run(self,):
        if self.done: return
        dep_tasks = [
             d.Run() for d in self.dependencies
        ]
        await asyncio.gather(*dep_tasks )
#        print (self, self.done, len(self.dependencies)
        success = True
        with OutputSender(self):
            await self.do_run()

        self.done = True

        return None

    def check_self(self,):
        raise RuntimeError("You must override this with a function that retunrs false if you need to  run the task")

    async def do_run(self,):
        raise RuntimeError("You must override this to provide your task")
