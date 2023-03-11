import unittest
import singleton
from singleton import Singleton

class TestModuleRegistration(unittest.TestCase):
    def setUp(self):
        self.test_module_1 = Singleton(1)
        self.test_module_2 = Singleton(256)
        self.test_module_3 = Singleton(53)

    def tearDown(self):
        if "module_register" in globals():
            global module_register
            del module_register

    def test_register_id(self):
        self.assertFalse("module_register" in globals())

        # Test that the method registers a module ID and updates the global module register
        self.assertEqual(self.test_module_1.own_modul_id, 1)
        self.assertEqual(self.test_module_2.own_modul_id, 256)
        self.assertEqual(self.test_module_3.own_modul_id, 53)
        self.assertEqual(len(singleton.get_module_register()), 3)
        self.assertEqual(singleton.get_module_register()[1], 256)

        # Test that the method appends additional module IDs to the global module register
        self.assertEqual(singleton.get_module_register()[0], 1)
        self.test_module_1._Singleton__register_id(12)
        self.assertEqual(len(singleton.get_module_register()), 3)
        self.assertEqual(singleton.get_module_register()[0], 12)

    def test_is_master(self):
        # check if modules are aware of the master module
        self.assertFalse(self.test_module_2.is_master())
        self.assertTrue(self.test_module_1.is_master())
        self.assertFalse(self.test_module_3.is_master())


if __name__ == '__main__':
    unittest.main()

