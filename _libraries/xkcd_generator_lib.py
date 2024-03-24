# region Import
from random import choice
from xkcdpass import xkcd_password
# endregion


# класс, реализующий генерирование паролей на основе библиотеки xkcd
# GitHub - https://github.com/redacted/XKCD-password-generator
# webcomic - https://xkcd.com/936/
class XKCD():
    # region ClassConst
    # wordlist - словарь
    # min_length / max_length - минимальная / максимальная длина слов в пароле 
    # valid_chars - доустимые символы
    # numwords=n - количество слов в пароле
    # delimiter - список разделителей
    # random_delimiters=True/False - использовать случайный разделитель
    # valid_delimiters - стандартный список разделителей
    # separator - сепаратор для разделения паролей
    # case - регистр слова

    # cписок разделителей: отдельно цифры, отдельно спецсимволы, отдельно скобки
    DELIMITERS_NUMBERS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    DELIMITERS_SPECIAL = ['!', '?', '"', '#', '$', '%', '&', '\'', '*', '+', ',', '.', '/', ':', ';', '=', '\\', '^', '|', '~', '-', '_']
    DELIMITERS_BRACKETS = ['(', ')', '[', ']', '{', '}', '<', '>']

    # пресеты генерируемых парольных фраз
    # numwords: количество слов, их которых состоит парльная фраза
    # case: регистр слов, используемых в парольной фразе ['lower', 'upper', 'alternating', 'random', 'capitalize', 'as-is']
    # random_delimiters: использовать случайные разделители слов в парольной фразе
    # valid_delimiters: список допустимых разделителей
    # delimiter: символ-разделитель между слов (фактически не используется, необходим только в пароле со сложностью weak, чтобы слова не были разделены пробелами)
    __PASSPHRASE_PRESETS = {
        'weak': {
            'numwords': 3,
            'case': 'lower',
            'random_delimiters': False,
            'valid_delimiters': '',
            'delimiter': ''
        },
        'standard': {
            'numwords': 4,
            'case': 'random',
            'random_delimiters': True,
            'valid_delimiters': DELIMITERS_NUMBERS,
            'delimiter': ''
        },
        'strong': {
            'numwords': 5,
            'case': 'capitalize',
            'random_delimiters': True,
            'valid_delimiters': DELIMITERS_NUMBERS + DELIMITERS_SPECIAL,
            'delimiter': ''
        },
        'super': {
            'numwords': 6,
            'case': 'capitalize',
            'random_delimiters': True,
            'valid_delimiters': DELIMITERS_NUMBERS + DELIMITERS_SPECIAL + DELIMITERS_BRACKETS,
            'delimiter': ''
        }
    }
    # endregion ClassConst

    # default constructor
    def __init__(self, filename:str=None):
        # загрузка словаря
        self.__wordlist = xkcd_password.generate_wordlist(
            wordfile=filename,
            valid_chars='[A-Za-z0-9]', 
            min_length=3,
            max_length=10,
        )

    def generate_passphrase(self, pwd_complexity:str) -> str:
        """
        Меетод создания пароля по заданной сложности параметрам
        :param pwd_complexity: сложность генерируемого пароля. Сложность аналогичная ключам словаря __PASSPHRASE_PRESETS.
            Используются только готовые пресеты
        :return: сгенерированный пароль заданной сложности
        """
        pwd_options = self.__PASSPHRASE_PRESETS.get(pwd_complexity)
        return xkcd_password.generate_xkcdpassword(
               wordlist=self.__wordlist,
               numwords=pwd_options["numwords"],
               case=pwd_options["case"],
               random_delimiters=pwd_options["random_delimiters"],
               valid_delimiters=pwd_options["valid_delimiters"],
               delimiter='' # pwd_options["valid_delimiters"]
        )

    def __weak(self):
        # Не используется. Метод генерации слабого пароля: 3 слова без раздетилей
        return xkcd_password.generate_xkcdpassword(
               wordlist=self.__wordlist,
               numwords=3, 
               delimiter='',
        )

    def __normal(self):
        # Не используется. Метод генерации слабого пароля: 4 слова, разделитель в виде случайной цифры
        return xkcd_password.generate_xkcdpassword(
            self.__wordlist,
            numwords=4,
            case='random',
            random_delimiters=True,
            valid_delimiters=self.DELIMITERS_NUMBERS
        )

    def __strong(self):
        # Не используется. Метод генерации слабого пароля: 5 слов и большой выбор разделителей  
        return xkcd_password.generate_xkcdpassword(
            self.__wordlist,
            numwords=5,
            case='random',
            random_delimiters=True,
            valid_delimiters=self.DELIMITERS_NUMBERS+self.DELIMITERS_SPECIAL
        )

    def __get_custom_password_params(self):
        yes_ans = ['', 'y', 'Y', 'yes', 'Yes', 'YES']

        print('Please, enter count (between 1 and 15) of word in password (4 words is default): ', end='')
        ans = input()
        count = int(ans) if ans != '' else 4

        print('Would you like to use separators in password (yes[default]/no)? ', end='')
        ans = input()
        is_separator = True if ans in yes_ans else False

        print('Would you like to use prefixes in password (yes[default]/no)? ', end='')
        ans = input()
        is_prefixes = True if ans in yes_ans else False

        return count, is_separator, is_prefixes

    def __custom(self):
        # Не используется. Метод генерации кастомных паролей
        delimiters_full = self.DELIMITERS_NUMBERS + self.DELIMITERS_SPECIAL
        # count: int, separators: bool, prefixes: bool
        count, separators, prefixes = self.__get_custom_password_params()
        # Произвольный пароль: сложность зависит от настроек пользователя
        pwd = xkcd_password.generate_xkcdpassword(
            self.__wordlist,
            numwords=count,
            case='random', 
            delimiter='',
            random_delimiters=separators, 
            valid_delimiters=delimiters_full
        )
        print(pwd)
        if prefixes == separators:
            return pwd
        elif separators and not prefixes:
            return pwd[1:-1]
        elif prefixes and not separators:
            return f'{choice(delimiters_full)}{pwd}{choice(delimiters_full)}'
