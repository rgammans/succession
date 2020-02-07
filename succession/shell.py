from . import job
import asyncio
from succession.exceptions import JobFailed


class ShellJob(job.Job):
    def __init__(self, **kwargs):
        self.command = kwargs.pop("command","")
        super().__init__(**kwargs)

    async def do_run(self,):
        proc = asyncio.create_subprocess_shell(self.command,
                stdout =  asyncio.subprocess.PIPE,
                stderr = asyncio.subprocess.PIPE,
        )
        self.out, self.err = await proc.communicate()
        if proc.returncode != 0:
            raise JobFailed(self)
 
