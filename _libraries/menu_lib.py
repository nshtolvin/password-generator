# region Import
from re import match

from _libraries.pwd_generator_lib import PwdGen
from _libraries import logger_lib
# endregion

class Menu():
    # default constructor
    def __init__(self, pwd_gen_obj:PwdGen) -> None:
        self.__pwd_gen = pwd_gen_obj
    
    def show_main_menu(self) -> None:
        # получаем список, содержащий пречень сложностей генерируемых парольных фраз - они же фактически определяют параметры парольных фраз
        # в данном контексте они необходимы для формирования пользовательского меню
        list_pwd_compl = self.__pwd_gen.get_passphrase_presets()
        pwd_count_defaults = self.__pwd_gen.CMD_OPTIONS_DEFAULTS["count"]
        
        while True:
            # вывод меню на основе списка list_pwd_compl
            print('Please, select password complexity:')
            for ind in range(len(list_pwd_compl)):
                print(f'    [{ind + 1}] {list_pwd_compl[ind].capitalize()}')
            print('\r\nPassphrase options')
            print('    [5] Show current custom passphrase options')
            print('    [6] Set custom passphrase options')
            print('    [7] Reset custom passphrase settings to defaults')
            print('[0] exit')

            # switcher = {1: 'weak', 2: 'standard', 3: 'strong', 4: 'custom'}
            # list_pwd_compl = {'weak', 'standard', 'strong', 'custom'}
            try:
                # считываем введенную пользователем сложность генерируемой парольной фразы или выбранный пункт меню
                compl_input = input('-> ')
                if int(compl_input) == 0: break
                if int(compl_input) == 5:
                    self.__pwd_gen.show_passphrase_options('custom')
                    continue
                if int(compl_input) == 6:
                    # задание кастомных (пользовательских) параметров парольной фразы
                    self.__pwd_gen.set_custom_passphrase_options()
                    continue
                if int(compl_input) == 7:
                    # сброс кастомных (пользовательских) параметров парольной фразы к дефолтным значениям
                    if self.__pwd_gen.reset_passphrase_options_to_defaults() == 0:
                        print(f'Custom passphrase settings have been restored to defauls.')
                        self.__pwd_gen.show_passphrase_options('custom')
                    else:
                        print('Error bringing custom passphrase settings to default values.')
                    continue
                # определяем сложность генерируемого пароля из пресетов (=str)
                compl = list_pwd_compl[int(compl_input) - 1]

                # считываем количество парольных фраз заданной сложности, которые необходимо сгенерировать
                # по умолчанию генерируется пять парольных фраз; максимально допускается сгенерировать 20 паролей
                print(f'Please, select the number of generated passphrases [{pwd_count_defaults["min_val"]}..{pwd_count_defaults["max_val"]}, default = {pwd_count_defaults["default"]}]: ',
                      end='')
                pwd_count = input()
                if match(r'^[0-9]+$', pwd_count) is None or int(pwd_count) not in range(pwd_count_defaults["min_val"], pwd_count_defaults["max_val"] + 1):
                    pwd_count = pwd_count_defaults["default"]
                
                print()
                pwd_options = self.__pwd_gen.get_passphrase_options(compl)
                # генерируем парольные фразы и выводим пользователю
                for ind in range(int(pwd_count)):
                    passphrase = self.__pwd_gen.generate_passphrase(pwd_options)
                    print(f"{''.join(passphrase[0])}\t {' '.join(passphrase[1])}")
                
                print(f'\r\n[Note]\r\nThe password is formed from the first {pwd_options["char_count"]} letters of each word.')
                print(f'Numbers are used only at the beginning of the password; special characters are used as separators between words')
            except Exception:
                logger_lib.error('User-Input Value', f'Something went wrong. Possibly an invalid user input!')
                continue
            except KeyboardInterrupt:
                break
            finally:
                print()
