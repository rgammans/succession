import unittest
import unittest.mock
import asyncio

from succession.job import Job

async def foo():pass
foo = foo()
coroutine = type(foo)
## Silence Never awaited warnings
try: foo.send(None)
except: pass

class MockJob(Job):
    def __init__(self, ok):
        self._ok = ok

    def Ok(self):
        return self._ok


class BaseJobTests(unittest.TestCase):
    def setUp(self,):
        self.j =  Job()

    def test_jobs_run_method_calls_Ok_first_and_doesnt_call_underrun_iftrue_return_a_completed_awaitbale(self,):
        with unittest.mock.patch.object(self.j,'Ok',return_value = True) as ok,\
             unittest.mock.patch.object(self.j,'_run',return_value = None) as run:
             rv  = self.j.Run()

        ok.assert_called_once_with()
        run.assert_not_called()
        self.assertIsInstance(rv,  ( asyncio.Future, asyncio.Task , coroutine ))
        ## Check the awaitable does nothing
        with self.assertRaises((StopIteration, GeneratorExit,)):
            rv.send(None)


    def test_jobs_run_method_calls_Ok_first_and_does_call_underrun_iffalse_and_returns_underruns_rv(self,):
        with unittest.mock.patch.object(self.j,'Ok',return_value = False) as ok,\
             unittest.mock.patch.object(self.j,'_run',return_value =unittest.mock.sentinel.RETVALUE) as run:
            rv = self.j.Run()

        ok.assert_called_once_with()
        run.assert_called_once_with()
        self.assertEqual(rv,unittest.mock.sentinel.RETVALUE)

    def test_under_run_retuns_an_awaitable(self,):

        out = self.j._run()
        self.assertIsInstance(out,  ( asyncio.Future, asyncio.Task , coroutine ))

        ## Silence Never awaited warnings
        try: out.send(None)
        except: pass



    def test_OK_calls_check_self_and_returns_if_false(self,):
        with unittest.mock.patch.object(self.j,'check_self',return_value = False) as ok:
            rv = self.j.Ok()

        ok.assert_called_once_with()
        self.assertEqual(rv,False)

    def test_OK_calls_check_self_and_calls_ok_on_deps_if_true(self,):
        for i in range(10):
            self.j.add_dependency(MockJob(True))

        with unittest.mock.patch.object(self.j,'check_self',return_value = True) as ok:
            rv = self.j.Ok()

        ok.assert_called_once_with()
        self.assertEqual(rv,True)

    def test_OK_calls_check_self_and_calls_ok_on_deps_if_true_It_only_take_one_dep_to_fail_Ok(self,):
        for i in range(10):
            self.j.add_dependency(MockJob(i == 9))

        with unittest.mock.patch.object(self.j,'check_self',return_value = True) as ok:
            rv = self.j.Ok()

        ok.assert_called_once_with()
        self.assertEqual(rv,False)


    def test_a_new_job_has_an_empty_deps_list(self,):
        self.assertEqual(len(self.j.dependencies),0)

    def test_add_depency_adds_it_argument_to_depencies(self,):
        self.j.add_dependency(unittest.mock.sentinel.NEW_DEP)
        self.assertIn( unittest.mock.sentinel.NEW_DEP, self.j.dependencies,)
