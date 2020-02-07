import unittest
import unittest.mock
import pathlib

from succession import filefilter
from succession import registry


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
