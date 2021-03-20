import unittest
import unittest.mock
import pathlib
import asyncio
import sys
from succession import shell
from succession.exceptions import JobFailed

class MockStream:
    def __init__(self,v):
        self.str_v = v

    def decode(self,):
        return self.str_v



class MockProcess:
    def __init__(self,rc, stdout, stderr):
        self.returncode = rc
        self.stdout = MockStream(stdout)
        self.stderr = MockStream(stderr)

    async def communicate(self, inp = None):
        return self.stdout, self.stderr

if sys.version_info.minor > 7:
    ## Chnages around unittest and aiountites means the 
    # waymocks work suggest that we don't need this as co-reoinr in 3.8 and later
    def getMockProcess(*args,**kwargs):
        return MockProcess(*args,**kwargs)
else:
     async def getMockProcess(*args,**kwargs):
        return MockProcess(*args,**kwargs)


class ShellJobTest(unittest.TestCase):

    def test_shell_job_calls_contstructs_the_job(self,):
        s = shell.ShellJob(command = unittest.mock.sentinel.SHELLCOMMAND)
        s.dependencies
        self.assertFalse(s.done)

    def test_shell_job_calls_x_to_run_its_command_string(self,):

        s = shell.ShellJob(command = unittest.mock.sentinel.SHELLCOMMAND)
        with unittest.mock.patch.object(asyncio,'create_subprocess_shell', return_value = getMockProcess(0,'','')) as runner:
            asyncio.run(s.do_run())

        runner.assert_called_once_with(
                unittest.mock.sentinel.SHELLCOMMAND,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
        )

    def test_shell_job_captures_stdin_stdout_of_command_string_can_removes_trailling_nls(self,):
        process = getMockProcess(0,
            "unittest.mock.sentinel.STDOUT\n",  ## These neeed to be strings
            "unittest.mock.sentinel.STDERR\n"
        )
        s = shell.ShellJob(command = unittest.mock.sentinel.SHELLCOMMAND)
        with unittest.mock.patch.object(asyncio,'create_subprocess_shell', return_value = process) as runner:
            asyncio.run(s.do_run())

        runner.assert_called_once_with(
                unittest.mock.sentinel.SHELLCOMMAND,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
        )

        self.assertEqual(s.out,  "unittest.mock.sentinel.STDOUT")
        self.assertEqual(s.err,  "unittest.mock.sentinel.STDERR" )

    def test_shell_job_raises_an_error_if_the_rc_is_nonzero(self,):
        s = shell.ShellJob(command = unittest.mock.sentinel.SHELLCOMMAND)
        with unittest.mock.patch.object(asyncio,'create_subprocess_shell', return_value = getMockProcess(1,'','')) as runner:
            with self.assertRaises(JobFailed):
                asyncio.run(s.do_run())


