# region Import
import sys
import textwrap
import argparse
from platform import system

from _libraries.pwd_generator_lib import PwdGen
from _libraries.menu_lib import Menu
# endregion


class ArgumentParser():
    # default constructor
    def __init__(self, dict_files_path:str, conf_filename:str) -> None:
        # инициализация объекта, раелизующего интерфейс командной строки
        self.__parser = None
        self.__args = None
        self.__init_parser_obj()

        # подготовка и инициализация объекта, реализующего непосредственно генерацию парольных фраз
        if system() == 'Windows':
            dict_files_path = dict_files_path + '/win'
        else:
            dict_files_path = dict_files_path + '/lin'
        self.__pwd_gen = PwdGen(dict_files_path, conf_filename)
    
    # default destructor
    def __del__(self):
        del self.__pwd_gen
        del self.__parser
    
    def __init_parser_obj(self,) -> None:
        """
        Инициализация объекта ArgumentParser, реализующего интерфейс командной строки (параметры, опции, аргументы) и
        автоматически генерирующего справочное сообщение и сообщения об использовании программы/утилиты.
        :return: None
        """
        # создание и инициализация объекта, реализующего интерфес командной строки. Задаются Описание и Эпилог с допустимыми примерами использования утилиты
        self.__parser = argparse.ArgumentParser(
            prog='pwdgen',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent("""\
                                        Simple console password generator.
                                        Examples of use are given at the end of the help message.
                                        """),
            epilog=textwrap.dedent("""\
                                Examples of acceptable use of the utility and its parameters.
                                Call a simple console control menu:
                                    pwdgen --main-menu
                                        
                                Generate passphrases with predefined complexity levels:
                                    pwdgen [--compl {weak,standard,strong}] [-c COUNT]
                                        
                                Generate passphrases with user (custom) parameters:
                                    pwdgen [-c COUNT] [-w WORD_COUNT] [-l LETTER_COUNT] [-n] [-s] [-u]""")
        )
        # добавление необходимых опций и их параметров (допустимые значения, значения по умолчанию, тип данных и прочее)
        self.__parser.add_argument('-m', '--main-menu',
                                   action='store_true',
                                   help='Call a simple console control menu')
        self.__parser.add_argument('--compl',
                                   choices=['weak', 'standard', 'strong'],
                                   default='standard',
                                   type=str,
                                   help='Complexity of the generated passphrase')
        self.__parser.add_argument('-c', '--count',
                                   choices=range(PwdGen.CMD_OPTIONS_DEFAULTS["count"]["min_val"], PwdGen.CMD_OPTIONS_DEFAULTS["count"]["max_val"] + 1),
                                   default=PwdGen.CMD_OPTIONS_DEFAULTS["count"]["default"],
                                   type=int,
                                   metavar='COUNT',
                                   help='Number of generated passphrases') 
        self.__parser.add_argument('-w', '--word-count',
                                   choices=range(PwdGen.CMD_OPTIONS_DEFAULTS["words_count"]["min_val"], PwdGen.CMD_OPTIONS_DEFAULTS["words_count"]["max_val"] + 1),
                                   default=PwdGen.CMD_OPTIONS_DEFAULTS["words_count"]["default"],
                                   type=int,
                                   metavar='WORD_COUNT',
                                   help='Number of words to be used in the passphrase')
        self.__parser.add_argument('-l', '--char-count',
                                   choices=range(PwdGen.CMD_OPTIONS_DEFAULTS["char_count"]["min_val"], PwdGen.CMD_OPTIONS_DEFAULTS["char_count"]["max_val"] + 1),
                                   default=PwdGen.CMD_OPTIONS_DEFAULTS["char_count"]["default"],
                                   type=int,
                                   metavar='CHAR_COUNT',
                                   help='Number of first letters of each word to be used in the passphrase')
        self.__parser.add_argument('-n', '--num',
                                   action='store_true',
                                   help='Use numbers as part of the passphrase')
        self.__parser.add_argument('-s', '--special-chars',
                                   action='store_true',
                                   help='Use special characters as part of the passphrase')
        self.__parser.add_argument('-u', '--upper-case',
                                   action='store_true',
                                   help='Use capital letters as part of the passphrase')

    def parse_arguments(self, ) -> None:
        """
        Обработчик введенной пользователем команды.
        Основную функцию обработки опций/параметров и их значений, ошибок и прочего реализует объект класса ArgumentParser.
        Далее реализуется логика обработки использованных опций в соответствии с тремя допустимыми шаблонами:
        1. Вызом простейшего консольного тестового меню
        2. Генерирование парольных фраз по предустановленным шаблонам
        3. Генерирование парольных фраз с пользовательскими (кастомными) настройками, переданными через опции утилиты
        :return: None
        """
        # обработки пользовательских опций в объекте ArgumentParser
        self.__args = self.__parser.parse_args()
        
        # логика обработки опций по допустимым шаблонам
        # использованы опции -m,--main-menu -> вызов консольного тестового меню. Имеет наивысший приоритет
        if self.__args.main_menu:
            # при использовании -m,--main-menu не допустимо использовать какие-либо дополнительные опции, поэтому длина массива sys.argv не может превышать 2
            # в противном случае - неверный формат ввода
            if len(sys.argv) == 2:
                menu = Menu(self.__pwd_gen)
                menu.show_main_menu()
                del menu
            else:
                self.__incorrect_cmd_options_handler()
        
        # использована опция --compl -> генерирование парольных фраз по предустановленным шаблонам
        elif '--compl' in sys.argv:
            # допустимо указание только шаблона сложности парольной фразы (длина массива sys.argv строго равна 3)
            # и/или число гененрируемых парольных фраз (длина sys.argv может быть увеличена до 5)
            # в противном случае - неверный формат ввода
            if len(sys.argv) == 3 or (len(sys.argv) == 5 and ('--count' in sys.argv or '-c' in sys.argv)):
                self.__print_passphrase(pwd_options=self.__pwd_gen.get_passphrase_options(self.__args.compl))
            else:
                self.__incorrect_cmd_options_handler()
        
        # особые случаи использования утилиты, требующие отдельного описания:
        # 1. вызов без параметров (длина sys.argv строго равна 1) - генерирование дефолтного числа парольных фраз по стандартному шаблону
        # 2. использованы толшько параметры -c,--count (длина sys.argv строго равна 3) - тождественно вызову утилиты в формате --compl COMPL -c COUNT, 
        #   описанному выше; из за явного отсутствия опиции --compl треует отдельной обработки
        elif len(sys.argv) == 1 or (len(sys.argv) == 3 and ('--count' in sys.argv or '-c' in sys.argv)):
            self.__print_passphrase(pwd_options=self.__pwd_gen.get_passphrase_options(self.__args.compl))
        
        # все прочие случаи - они же описывают использование всех прочих опций при вызове утилиты и реализуют пользовательские (кастомные) настройки парольных фраз
        else:
            self.__print_passphrase(pwd_options={'words_count': self.__args.word_count,
                                               'char_count': self.__args.char_count,
                                               'use_numbers': self.__args.num,
                                               'use_special': self.__args.special_chars,
                                               'use_upper_case': self.__args.upper_case})

    def __incorrect_cmd_options_handler(self, ) -> None:
        """
        Простейший обработчик, вызываемый в случае некорректного ииспользования опций утилиты. Вызывается в случае, если формат команды,
        полученный от пользлвателя, не соответствует форматам, приведенным в описании метода parse_arguments()
        :return: None
        """
        print('Unsupported format for using the utility. Please see examples in help message.\r\n')
        self.__parser.print_help()
    
    def __print_passphrase(self, pwd_options:dict) -> None:
        """
        Метод для выполнения запроса для генерации паролей и вывода сгенерированных паролей
        :param pwd_options: словарь с параметрами генерируемой парольной фразы
        :return: None
        """
        # генерируем парольные фразы и выводим пользователю
        for ind in range(int(self.__args.count)):
            passphrase = self.__pwd_gen.generate_passphrase(pwd_options)
            print(f"{''.join(passphrase[0])}\t {' '.join(passphrase[1])}")
        
        print(f'\r\n[Note]\r\nThe password is formed from the first {pwd_options["char_count"]} letters of each word.')
        print(f'Numbers are used only at the beginning of the password; special characters are used as separators between words')
