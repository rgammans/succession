import asyncio

async def nothing_to_do():
    return


class Job:
    def __init__(self,):
        self.dependencies = []

    def add_dependency(self, newdep):
        self.dependencies.append(newdep)

    def Ok(self):
        return ( self.check_self() and
                all( d.Ok() for d in self.dependencies ))

    def Run(self,):
        """Return completion promise for upto date ness of this job"""
        if not self.Ok():
            return self._run()
        else:
            return nothing_to_do()

    async def _run(self,):
        pass

    def check_self(self,):
        raise RuntimeError("You must override this with a function that retunrs false if you need to  run the task")

