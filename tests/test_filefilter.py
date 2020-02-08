import unittest
import unittest.mock
import pathlib

from succession import filefilter
from succession import registry

class MockStatResult:
    def __init__(self, mtime):
        self.st_mtime = mtime

class MockPath:
    def __init__(self, mtime):
        self.mtime = mtime

    def stat(self,):
        return MockStatResult(self.mtime)

class FileFilterJobTestCase(unittest.TestCase):
    def setUp(self,):
        registry.reset()

    def test_filefilter_take_source_and_target_and_records_paths(self,):
        j = filefilter.FileFilterJob(source="file_a", target="file_b")
        self.assertEqual(j.source, pathlib.Path("file_a").resolve())
        self.assertEqual(j.target, pathlib.Path("file_b").resolve())

    def test_filefilter_take_source_and_target_path(self,):
        j = filefilter.FileFilterJob(source=pathlib.Path("file_a"), target=pathlib.Path("file_b"))

    def test_filefilterjob_is_a_registered_job(self,):
        j = filefilter.FileFilterJob(source=pathlib.Path("file_a"), target=pathlib.Path("file_b"))
        self.assertIsInstance(j,registry.RegisteredJob)

    def test_filefilterjob_has_it_source_as_a_dependency(self,):
        j = filefilter.FileFilterJob(source=pathlib.Path("file_a"), target=pathlib.Path("file_b"))
        self.assertEqual(j.unresolved ,{ pathlib.Path("file_a").resolve() } )
    
    def test_filefilterjob_check_self_calls_stat_and_returns_true_if_target_newer(self,):
        j = filefilter.FileFilterJob(source=pathlib.Path("file_a"), target=pathlib.Path("file_b"))
        with unittest.mock.patch.object(j,'source', MockPath(1) ) as src,\
             unittest.mock.patch.object(j,'target', MockPath(2) ) as dst:


            self.assertTrue(j.check_self())

    def test_filefilterjob_check_self_calls_stat_and_returns_false_if_target_older(self,):
        j = filefilter.FileFilterJob(source=pathlib.Path("file_a"), target=pathlib.Path("file_b"))
        with unittest.mock.patch.object(j,'source', MockPath(2) ) as src,\
             unittest.mock.patch.object(j,'target', MockPath(1) ) as dst:


            self.assertFalse(j.check_self())


        #src.assert_called_once_with()
        #dst.assert_called_once_with()

