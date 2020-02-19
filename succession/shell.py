from . import job
import asyncio
from succession.exceptions import JobFailed


class ShellJob(job.Job):
    """Create a Job form a Shell command.

    A ShellJob is a job which executes a shell command.
    A Shell job captures stdout and stderr from the the run subprocess, and
    records them as the Jobs out, and err data respectively.

    If the sub process returns and exitcode other than 0, the job is
    consider to have failed and a JobFailed() exception is raised.

    :param command str: Command from by the default system shell,

    """
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

