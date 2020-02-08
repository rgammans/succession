import asyncio

async def nothing_to_do():
    return


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
        await self.do_run()
        print (self.out)
  #      print (self.err, file=sys.stderr)
        self.done = True

        return None

    def check_self(self,):
        raise RuntimeError("You must override this with a function that retunrs false if you need to  run the task")

    async def do_run(self,):
        raise RuntimeError("You must override this to provide your task")
