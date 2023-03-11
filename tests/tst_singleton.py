import unittest
import singleton
from singleton import Singleton

class TestModuleRegistration(unittest.TestCase):
    def setUp(self):
        self.test_module = Singleton(1)
        global module_register
        module_register = []

    def test_register_id(self):
        # Test that the method registers a module ID and updates the global module register
        global module_register
        self.test_module._Singleton__register_id(210)
        self.assertEqual(self.test_module.own_modul_id, 210)
        self.assertEqual(len(singleton.get_module_register()), 2)
        self.assertEqual(singleton.get_module_register()[1], 210)

        # Test that the method appends additional module IDs to the global module register
        self.test_module._Singleton__register_id(12)
        self.assertEqual(len(singleton.get_module_register()), 3)
        self.assertEqual(singleton.get_module_register()[2], 12)

        # Test that the method creates a new global module register if it doesn't exist
        del module_register
        self.test_module._Singleton__register_id(654)
        self.assertEqual(len(singleton.get_module_register()), 1)
        self.assertEqual(singleton.get_module_register()[0], 654)


if __name__ == '__main__':
    unittest.main()

