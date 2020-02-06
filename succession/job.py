import asyncio

async def nothing_to_do():
    return


class Job:
    def Ok(self):
        pass

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

