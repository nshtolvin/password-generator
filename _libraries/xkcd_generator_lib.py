# region Import
from random import choice
from xkcdpass import xkcd_password
# endregion


class XKCD():
    # wordlist - словарь
    # numwords=n - количество слов в пароле
    # delimiter - спасок разделителей
    # random_delimiters=False,
    # valid_delimiters - стандпртный список разделителей
    # case - регистр слова

    # Весь список разделителей, отдельно цифры, отдельно – спецсимволы
    delimiters_numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    delimiters_full = ['!', '$', '%', '^', '&', '*', '-', '_', '+', '=', ':', '|', '~', '?', '/', '.', ';'] + delimiters_numbers

    # default constructor
    def __init__(self, filename: str):
        # Загрузка словаря
        self.wordlist = xkcd_password.generate_wordlist(
            wordfile=filename,
            valid_chars='[a-z]', 
            min_length=4,
            max_length=10,
        )

    def weak(self):
        # Слабый пароль: 3 слова без раздетилей
        return xkcd_password.generate_xkcdpassword(
               self.wordlist,
               numwords=3, 
               delimiter='',
        )

    def normal(self):
        # Средний пароль: 4 слова, разделитель в виде случайной цифры
        return xkcd_password.generate_xkcdpassword(
            self.wordlist,
            numwords=4,
            case='random',
            random_delimiters=True,
            valid_delimiters=self.delimiters_numbers
        )

    def strong(self):
        # Сильный пароль: 5 слов и большой выбор разделителей  
        return xkcd_password.generate_xkcdpassword(
            self.wordlist,
            numwords=5,
            case='random',
            random_delimiters=True,
            valid_delimiters=self.delimiters_full
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

    def custom(self):
        # count: int, separators: bool, prefixes: bool
        count, separators, prefixes = self.__get_custom_password_params()
        # Произвольный пароль: сложность зависит от настроек пользователя
        pwd = xkcd_password.generate_xkcdpassword(
            self.wordlist,
            numwords=count,
            case='random', 
            delimiter='',
            random_delimiters=separators, 
            valid_delimiters=self.delimiters_full
        )
        print(pwd)
        if prefixes == separators:
            print(pwd)
            return pwd
        elif separators and not prefixes:
            print(pwd)
            return pwd[1:-1]
        elif prefixes and not separators:
            print(pwd)
            return f'{choice(self.delimiters_full)}{pwd}{choice(self.delimiters_full)}'