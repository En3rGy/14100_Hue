# import logging

def get_module_register():
    global module_register  # type: []
    if not isinstance(module_register, list):
        module_register = []

    return module_register


class Singleton:

    def __init__(self, module_id):
        """

        :param module_id:
        :type module_id: int
        """
        if not isinstance(module_id, int):
            raise TypeError("Expected an integer value")

        self.index = 0  # type: int
        self.own_modul_id = 0  # type: int

        global module_register
        if 'module_register' not in globals():
            module_register = []

        # already registered?
        if module_id in module_register:
            self.own_modul_id = module_id
        else:
            global module_count  # type: int
            if 'module_count' in globals():
                module_count = module_count + 1
            else:
                module_count = 1

            self.index = module_count
            self.__register_id(module_id)

    def is_master(self):
        return self.index == 1

    def __register_id(self, modul_id):
        global module_register
        if isinstance(module_register, list):
            if self.own_modul_id in module_register:
                module_register[module_register.index(self.own_modul_id)] = modul_id
            else:
                module_register.append(modul_id)
        else:
            module_register = [modul_id]

        self.own_modul_id = modul_id
