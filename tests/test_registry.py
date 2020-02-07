import unittest
import unittest.mock
import asyncio
import aiounittest

from succession import registry
from succession import job

class RegistryRealbasic(unittest.TestCase):
    """Test the basic reset and len functions
    this testcase test the functions used to
    ensure the main tests are truley independent.

    If these fail the RegistryTests TestCase is unreliable
    """
    def test_registry_has_zero_len_after_reset(self,):
        registry.reset()
        self.assertEqual(registry.size(),0)


    def test_registry_hasnt_get_an_added_job_after_reset(self,):
        registry.add_target("name",None)
        registry.reset()
        self.assertFalse(registry.has_target("name"))

class RegistryTests(unittest.TestCase):

    def setUp(self,):
        registry.reset()

    def test_add_target_adds_an_item_to_the_registy(self,):
        registry.add_target("name",None)
        #White box
        self.assertIn("name",registry._registry_store)

    def test_add_target_adds_a_rrasies_an_error_if_target_already_exists_andjob_is_different(self,):
        registry.add_target("name",None)
        with self.assertRaises(KeyError):
            registry.add_target("name",1)

    def test_add_target_adds_a_nops_if_target_already_exists_andjob_is_the_same(self,):
        registry.add_target("name",None)
        x = registry.size()
        registry.add_target("name",None)
        self.assertEqual(registry.size(),x)

    def test_has_target_returns_true_if_target_has_been_added(self,):
        registry.add_target("name",None)
        self.assertTrue(registry.has_target("name"))

    def test_has_target_returns_false_if_target_hasnt_been_added(self,):
        ## This is really duplciate by the base tests; but lets kepp it here
        #  as it puts the prmiamry function tests all in one place
        self.assertFalse(registry.has_target("name"))

    def test_find_target_returns_associated_if_target_has_been_added(self,):
        registry.add_target("name", unittest.mock.sentinel.JOB)
        self.assertEqual(registry.find_target("name"),unittest.mock.sentinel.JOB)

class RegsiteredJobTests(unittest.TestCase):

    def setUp(self,):
        registry.reset()


    def test_can_create_a_registered_job_with_a_target(self,):
        j = registry.RegisteredJob(target=unittest.mock.sentinel.TARGET)
        self.assertTrue(j.target, unittest.mock.sentinel.TARGET)
        self.assertIsInstance(j, job.Job)
        self.assertFalse(j.done)

    def test_creating_a_registered_job_registers_it_in_the_registry(self,):
        j = registry.RegisteredJob(target=unittest.mock.sentinel.TARGET)
        self.assertTrue(registry.has_target(unittest.mock.sentinel.TARGET))

    def test_adding_a_non_job_depencise_a_registered_job_loks_up_the_job_in_the_registry(self,):
        j1 = registry.RegisteredJob(target=unittest.mock.sentinel.TARGET_ONE)
        j2 = registry.RegisteredJob(target=unittest.mock.sentinel.TARGET_TWO)
        j2.add_dependency(unittest.mock.sentinel.TARGET_ONE)
        self.assertIn(j1,j2.dependencies)


    def test_adding_a_non_job_depencise_a_unregistered_job_stores_job_adds_the_job_when_resolve_called(self,):
        j2 = registry.RegisteredJob(target=unittest.mock.sentinel.TARGET_TWO)
        j2.add_dependency(unittest.mock.sentinel.TARGET_ONE)
        self.assertEqual(len(j2.dependencies),0)

        j1 = registry.RegisteredJob(target=unittest.mock.sentinel.TARGET_ONE)
        j2.resolve_dependencies()
        self.assertIn(j1,j2.dependencies)

    def test_adding_a_non_job_depencise_a_unregistered_job_reaises_a_key_error_if_defer_turned_off(self,):
        j2 = registry.RegisteredJob(target=unittest.mock.sentinel.TARGET_TWO, no_deferred_dependencies = True)
        with self.assertRaises(KeyError):
            j2.add_dependency(unittest.mock.sentinel.TARGET_ONE)

