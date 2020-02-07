import unittest
import unittest.mock
import pathlib
import asyncio
from succession import shell
from succession.exceptions import JobFailed

class MockProcess:
    def __init__(self,rc, stdout, stderr):
        self.returncode = rc
        self.stdout = stdout
        self.stderr = stderr

    async def communicate(self, inp = None):
        return self.stdout, self.stderr


class ShellJobTest(unittest.TestCase):

    def test_shell_job_calls_contstructs_the_job(self,):
        s = shell.ShellJob(command = unittest.mock.sentinel.SHELLCOMMAND)
        s.dependencies
        self.assertFalse(s.done)

    def test_shell_job_calls_x_to_run_its_command_string(self,):

        s = shell.ShellJob(command = unittest.mock.sentinel.SHELLCOMMAND)
        with unittest.mock.patch.object(asyncio,'create_subprocess_shell', return_value = MockProcess(0,'','')) as runner:
            asyncio.run(s.do_run())

        runner.assert_called_once_with(
                unittest.mock.sentinel.SHELLCOMMAND,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
        )

    def test_shell_job_captures_stdin_stdout_of_command_string(self,):
        process = MockProcess(0,
            unittest.mock.sentinel.STDOUT,
            unittest.mock.sentinel.STDERR
        )
        s = shell.ShellJob(command = unittest.mock.sentinel.SHELLCOMMAND)
        with unittest.mock.patch.object(asyncio,'create_subprocess_shell', return_value = process) as runner:
            asyncio.run(s.do_run())

        runner.assert_called_once_with(
                unittest.mock.sentinel.SHELLCOMMAND,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
        )

        self.assertEqual(s.out,  unittest.mock.sentinel.STDOUT)
        self.assertEqual(s.err, unittest.mock.sentinel.STDERR )

    def test_shell_job_raises_an_error_if_the_rc_is_nonzero(self,):
        s = shell.ShellJob(command = unittest.mock.sentinel.SHELLCOMMAND)
        with unittest.mock.patch.object(asyncio,'create_subprocess_shell', return_value = MockProcess(1,'','')) as runner:
            with self.assertRaises(JobFailed):
                asyncio.run(s.do_run())


