import unittest
import unittest.mock
import pathlib
from succession import cli
from succession import registry



class TestJobResolution(unittest.TestCase):

    def test_find_job_finds_the_target_named_default_ifexists_and_none_specified(self,):
        correctjob = unittest.mock.sentinel.DEFTARGET
        jr = cli.JobResolver(None)
        with unittest.mock.patch.object(cli, 'find_target', 
                return_value = correctjob) as ft:
            job =  jr.find_job()

        self.assertEqual(job, correctjob)
        ft.assert_called_once_with("default")

    def test_find_job_finds_the_target_with_speficed_name_ifexists(self,):
        correctjob = unittest.mock.sentinel.DEFTARGET
        jobname = unittest.mock.sentinel.JOBNAME
        jr = cli.JobResolver(jobname)
        with unittest.mock.patch.object(cli, 'find_target', 
                return_value = correctjob) as ft:
            job =  jr.find_job()

        self.assertEqual(job, correctjob)
        ft.assert_called_once_with(jobname)

    def test_find_job_finds_the_default_target_iif_specificed_name_notexists(self,):
        correctjob = unittest.mock.sentinel.DEFTARGET
        jobname = unittest.mock.sentinel.JOBNAME
        jr = cli.JobResolver(jobname)
        with unittest.mock.patch.object(cli, 'find_target', 
                side_effect = [ KeyError, correctjob]) as ft:
            job =  jr.find_job()

        self.assertEqual(job, correctjob)
        ft.assert_has_calls([ unittest.mock.call(jobname) , unittest.mock.call('default')],any_order = False)

    def test_find_job_finds_the_smae_name_file_target_iif_specificed_name_notexists_anf_the_path_exists(self,):
        correctjob = unittest.mock.sentinel.DEFTARGET
        jobname = 'file_a'
        jr = cli.JobResolver(jobname)
        with unittest.mock.patch.object(cli, 'find_target', 
                side_effect = [ KeyError, correctjob]) as ft:
            job =  jr.find_job()

        self.assertEqual(job, correctjob)
        ft.assert_has_calls([ unittest.mock.call(jobname) , unittest.mock.call(pathlib.Path(jobname))],any_order = False)

    def test_find_job_raises_runtime_error_if_no_target_found(self,):
        correctjob = unittest.mock.sentinel.DEFTARGET
        jobname = 'file_a'
        jr = cli.JobResolver(jobname)
        with unittest.mock.patch.object(cli, 'find_target', 
                side_effect = KeyError) as ft:
            with self.assertRaises(RuntimeError):
                job =  jr.find_job()

