import unittest
import unittest.mock
import asyncio
import aiounittest

from succession.job import Job

async def empty_coroutine_gen():pass
empty_coroutine = empty_coroutine_gen()
coroutine = type(empty_coroutine)
## Silence Never awaited warnings
try: empty_coroutine.send(None)
except: pass

class MockJob(Job):
    def __init__(self, ok, task= None):
        super().__init__()
        self.has_run = False
        self._ok = ok
        self.task = task

    def Ok(self):
        return self._ok

    def Run(self,):
        self.has_run = True
        return empty_coroutine_gen()

    async def do_run(self,):
        if self.task:
            await self.task()

class AlwaysDoNothing(Job):
    def check_self(self,):
        return False

    async def do_run(self,):
        return None

class BaseJobTests(unittest.TestCase):
    def setUp(self,):
        self.j =  AlwaysDoNothing()
#
#    def tearDown(self,):
#        ## CLeanup event loop, which doesn't walasy happen
#        loop = None
#        try:
#            loop = asyncio.get_event_loop()
#        except RuntimeError:pass
#        if loop:
#            loop.close()

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


    def test_dunder_run_call_Run_on_all_it_dependencies_when_they_need_to_run(self,):
        deps = []
        for i in range(10):
            x = MockJob(False)
            deps.append(x)
            self.j.add_dependency(x)

        self.j.do_run = empty_coroutine_gen
        asyncio.run(self.j._run())
        for x in deps:
            self.assertTrue(x.has_run)

    def test_dunder_run_call_Run_on_all_it_dependencies_when_they_dont_need_to_run(self,):
        deps = []
        for i in range(10):
            x = MockJob(True)
            deps.append(x)
            self.j.add_dependency(x)

        self.j.do_run = empty_coroutine_gen
        asyncio.run(self.j._run())
        for x in deps:
            self.assertTrue(x.has_run)

    def test_under_awaits_do_run_when_there_are_no_deps(self,):
        with unittest.mock.patch.object(self.j,'do_run',return_value = empty_coroutine_gen()) as runner:
            asyncio.run(self.j._run())

        runner.assert_called_once_with()


    @aiounittest.async_test
    async def test_under_run_calls_do_run_only_after_deps_are_completed(self,):
        ### Create some dependencies which we can use to pause the 
        #   resolution.
        deps = []

        ## Create  task which can't complete .
        block = asyncio.Lock()
        def task():
            with block:
                return None

        for i in range(10):
            x = MockJob(False, task = task)
            deps.append(x)
            self.j.add_dependency(x)

        await block.acquire()
        with unittest.mock.patch.object(self.j,'do_run',return_value = empty_coroutine_gen()) as runner:
            # Launch self.j._run()
            completion = self.j._run()
            # sleep.
            await asyncio.sleep(1)
#            await asyncio.sleep(1)
            runner.assert_not_called()
            # Release dependent blockers
            block.release()
            # Wait for _run() to complete
            await completion
            # Check j.do_run has_been_called
            runner.assert_called_once_with()

    @aiounittest.async_test
    async def test_the_bottom_task_in_a_diamond_dependency_pattern_is_only_run_once(self,):
        ## Build diamond
        end_task = AlwaysDoNothing()
        task_a = AlwaysDoNothing()
        task_b = AlwaysDoNothing()
        task_a.add_dependency(end_task)
        task_b.add_dependency(end_task)
        self.j.add_dependency(task_a)
        self.j.add_dependency(task_b)
        with unittest.mock.patch.object(end_task,'do_run',side_effect = empty_coroutine_gen) as runner:
            await self.j._run()

        runner.assert_called_once_with()


    def test_job_has_out_and_err_attributes_to_store_messages_from_run(self,):
        self.j.out
        self.j.err
