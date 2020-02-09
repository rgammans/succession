from . import job
import asyncio
from succession.exceptions import JobFailed


class ShellJob(job.Job):
    def __init__(self, **kwargs):
        self.command = kwargs.pop("command","")
        super().__init__(**kwargs)

    async def do_run(self,):
        proc = await asyncio.create_subprocess_shell(self.command,
                stdout =  asyncio.subprocess.PIPE,
                stderr = asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        self.out, self.err = stdout.decode().rstrip(), stderr.decode().rstrip()
        if proc.returncode != 0:
            raise JobFailed(self)
 
