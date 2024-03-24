# region Import
from random import SystemRandom
from math import pow
from re import match

from _libraries.dict_worker_lib import DictFileWorker
from _libraries.configuration_lib import Config
from _libraries import logger_lib
# endregion


# класс, реализующий генерирование паролей на основе слов русского языка
class PwdGen(DictFileWorker, Config):    
    # region ClassConst
    # атрибуты класса PwdGen; часть из них фактически является константами
    # части речи слов, которые могут использоваться в составе пароля [прилагательное, наречие, существительное, числительное, глагол]
    PARTS_OF_SPEECH = ['ADJF', 'ADVB', 'NOUN', 'NUMR', 'INFN']

    # наборы символов, которые могут использоваться в составе генерируемого праоля (помимо букв латинского алфавита)
    NUMBERS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    MINUS = ['-']
    UNDERLINE = ['_']
    SPECIAL = ['!', '?', '"', '#', '$', '%', '&', '\'', '*', '+', ',', '.', '/', ':', ';', '=', '\\', '^', '|', '~']
    BRACKETS = ['(', ')', '[', ']', '{', '}', '<', '>']

    # шаблоны генерируемых парольных фраз - предствляют собой последовательность частей речи
    __PASSPHRASE_PATTERNS = {
        2: f'ADJF NOUN',
        3: f'NOUN INFN NOUN',
        4: f'ADJF NOUN INFN NOUN',
        5: f'ADJF NOUN INFN ADJF NOUN',
        6: f'ADJF NOUN ADVB INFN ADJF NOUN'
    }
    # пресеты генерируемых парольных фраз
    # words_count: количество слов, их которых состоит парльная фраза
    # char_count: количество букв каждого слова, которые используются в генерируемом пароле
    # is_numbers: использовать цифры в составе парольной фразы (в качестве разделителя, префикса или постфикса)
    # is_special: использовать дополнительные символы (спецсимволы) в составе парольной фразы (в качестве разделителя, префикса или постфикса)
    # use_upper_case: использовать заглавную букву в начале каждого слова парольной фразы
    __PASSPHRASE_PRESETS = {
        'weak': {
            'words_count': 3,
            'char_count': 3,
            'use_numbers': False,
            'use_special': False,
            'use_upper_case': False
        },
        'standard': {
            'words_count': 4,
            'char_count': 3,
            'use_numbers': True,
            'use_special': False,
            'use_upper_case': True
        },
        'strong': {
            'words_count': 5,
            'char_count': 4,
            'use_numbers': True,
            'use_special': True,
            'use_upper_case': True
        },
        # занчения по умолчанию для пользовательских (кастомных) параметров парольной фразы
        'custom': {
            'words_count': 4,
            'char_count': 3,
            'use_numbers': True,
            'use_special': False,
            'use_upper_case': False
        }
    }

    CMD_OPTIONS_DEFAULTS = {
        'count': {'min_val': 1, 'max_val': 20, 'default': 5},
        'words_count': {'min_val': 2, 'max_val': 6, 'default': 4},
        'char_count': {'min_val': 3, 'max_val': 5, 'default': 3},
        'use_numbers': {'default': False},
        'use_special': {'default': False},
        'use_upper_case': {'default': False},
    }
    # endregion ClassConst

    # default constructor
    def __init__(self, dict_files_path:str, conf_filename:str) -> None:
        # super().__init__()
        # super(DictFileWorker, self).__init__()
        DictFileWorker.__init__(self)
        # при вызове конструктора базового класса Config передаются словарь с дефолтными параметрами кастомных паролей на случай возвращения к ним 
        Config.__init__(self, conf_filename, self.__PASSPHRASE_PRESETS["custom"])
        self.__randomizer = SystemRandom()
        self.__dictionaries_filenames = {
            'ADJF': f'{dict_files_path}/adjectives.txt',
            'ADVB': f'{dict_files_path}/adverb.txt',
            'NOUN': f'{dict_files_path}/nouns.txt',
            'NUMR': f'{dict_files_path}/numeral.txt',
            'INFN': f'{dict_files_path}/verbs.txt'
        }

        # обновляем пользовательские (кастомные) параметры парольной фразы, занося из в словарь __PASSPHRASE_PRESETS
        # параметры хранятся в поле радительского класса Config и были предварительно считаны из conf.ini
        custom_options = self.get_options()
        self.__update_custom_passphrase_options(options=custom_options, is_upd_file=False)
    
    # default destructor
    def __del__(self):
        del self.__randomizer
        super().__del__()
        # super(DictFileWorker, self).__del__()
        # super(Config, self).__del__()
    
    def get_passphrase_presets(self) -> list:
        """
        Метод для получения списка, содержащего возможные (допустимые) сложности генерируемых парольных фраз из ключей словаря __PASSPHRASE_PRESETS
        :return: возможные сложности генерируемых парольных фраз (список)
        """
        return list(self.__PASSPHRASE_PRESETS.keys())
    
    def get_passphrase_options(self, pwd_complexity:str) -> dict:
        """
        Метод для получения опций (параметров) парольной фразы исходя из заданного уровня сложности парольной фразы
        :param pwd_complexity: сложность парольный фразы, параметры которой необходимо получить
        :return: словарь опций (парметров) и их значений для парольной фразы заданной сложности
        """
        return self.__PASSPHRASE_PRESETS.get(pwd_complexity)

    def generate_passphrase(self, pwd_options:dict) -> list:
        """
        Меетод создания парольной фразы по заданным параметрам
        :param pwd_options: словарь с параметрами генерируемой парольной фразы.
            Параметры аналогичны ключам словаря PASSPHRASE_PRESETS. Могут использоваться готовые пресеты или пользовательские настройки
        :return: список сгенерированных парольных фраз
        """
        # определяем шаблон парольной (сложность парольной фразы определяет количество слов в ней, и как следствие - используемый шаблон парольной фразы)
        pwd_ptrn_prts = (self.__PASSPHRASE_PATTERNS.get(pwd_options["words_count"])).split()

        # список для хранения слов парольнаой фразы на русском языке
        rus_passphrase = list()
        # генерация слов, которые войдут в парольную фразу
        for prt in pwd_ptrn_prts:
            rus_passphrase.append(self.__get_random_word(prt).lower())
                
        # получение слов парольной фразы на английском языке
        eng_passphrase = self.__change_layout(rus_passphrase)
                
        # отсекаем первые char_count каждого слова парольной фразы
        eng_passphrase = [word[:pwd_options["char_count"]] for word in eng_passphrase]

        # при необходимости меняем регистр первой бкувы каждого слова
        if pwd_options["use_upper_case"]:
            rus_passphrase = self.__set_upper_case(rus_passphrase)
            eng_passphrase = self.__set_upper_case(eng_passphrase)
                
        # при необходимости добавляем специальные символы в паролную фразу
        if pwd_options["use_special"]:
            # определяем количество специльных символов, которые будут добавлены в парольную фразу
            # с учетом того, что при трансляции слова с русского языка на английский возможно появление специальных символов, программно
            # ограничиваем максимально возможное число добавляемых спецсимволов
            specials_count = self.__randomizer.randint(1, 4)
            for ind in range(specials_count):
                # выбираем специальный символ
                spec_ch = self.__randomizer.choice(self.SPECIAL)
                # определяем позицию, куда специальный символ будет вставлен
                pos = self.__randomizer.randint(0, len(rus_passphrase) + 1)
                # добавляем специальный символ в парольную фразу
                rus_passphrase.insert(pos, spec_ch)
                eng_passphrase.insert(pos, spec_ch)

        # при необходимости добавляем цифры в паролную фразу (пока цифры добавляются только в начало парольной фразы)
        if pwd_options["use_numbers"]:
            # определяем количество цифр, которые будут добавлены в парольную фразу
            numbers_count = self.__randomizer.randint(1, 4)
            number = 0
            for ind in range(numbers_count):
                number = number + (int(self.__randomizer.random() * 10) * int(pow(10, ind)))
            rus_passphrase.insert(0, str(number))
            eng_passphrase.insert(0, str(number))

        return [eng_passphrase, rus_passphrase]
    
    def __change_layout(self, pwd_prts:list) -> list:
        """
        Изменение языка слов, которые будут использоваться в составе парольной фразы. Изменение языка подразумевает замену русских букв на английские
        в соответствии с клавишами клавиатуры 
        :param pwd_prts: исходный список слов парольной фразы
        :return: преобразованный (замена русских букв на английские) список слов парольной фразы
        """
        # region Const
        RUS_LAYOUT = 'йцукенгшщзхъфывапролджэячсмитьбюёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮЁ'
        ENG_LAYOUT = 'qwertyuiop[]asdfghjkl;\'zxcvbnm,.`QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>~'
        # endregion

        tr_pwd_prts = list()
        # цикл по элементам списка слов, входящих в парольную фразу
        for ind in range(len(pwd_prts)):
            # далее буквы русского языка заменяются на буквы английского в соответствии с раскладкой
            # инициализация слова парольной фразы после изменения
            tr_wrd = ''
            # цикл, где выполняется замена букв
            for ltr in pwd_prts[ind]:
                tr_wrd = tr_wrd + ENG_LAYOUT[RUS_LAYOUT.find(ltr)]
            # pwd_prts[ind] = tr_wrd
            tr_pwd_prts.append(tr_wrd)
        return tr_pwd_prts

    def __set_upper_case(self, pwd_prts:list) -> list:
        """
        Изменение регистра первой буквы каждого слова, которое будет использоваться в составе парольной фразы
        :param pwd_prts: исходный список слов парольной фразы
        :return: преобразованный (первая буква слова - заглавная) список слов парольной фразы
        """
        return [wrd.capitalize() for wrd in pwd_prts]

    def __get_random_word(self, prt_of_sppech:str) -> str:
        """
        Выбор случайного слова из словаря слов заданной части речи. Считанный файл сичтывается полностью; после из него случайным образом выбирется одно слово. 
        В конце необходимо удалить символ новой строки (\n) для выбранного слова.
        :param prt_of_sppech: [сокращение ~ часть речь] условное обозначение (сокращение) словаря, из которого будут считываться данные (строки)
        :return: случайное слово из словаря, которое далее будет использоваться в составе пароля
        """
        dict_content = self._read_dict_file(self.__dictionaries_filenames[prt_of_sppech])
        return self.__randomizer.choice(dict_content)[:-1]
    
    def show_passphrase_options(self, compl:str) -> None:
        """
        Вывод параметров парольной фразы
        :param compl: сложность парольной фразы, параметры которой будут выводиться
        :return: None
        """
        print(f'Current {compl} passphrase options:')
        print(f'    words count - {self.__PASSPHRASE_PRESETS[compl]["words_count"]}')
        print(f'    chars count - {self.__PASSPHRASE_PRESETS[compl]["char_count"]}')
        print(f'    use of numbers - {self.__PASSPHRASE_PRESETS[compl]["use_numbers"]}')
        print(f'    use of special characters - {self.__PASSPHRASE_PRESETS[compl]["use_special"]}')
        print(f'    capitalize the first letter of each word - {self.__PASSPHRASE_PRESETS[compl]["use_upper_case"]}')
    
    def set_custom_passphrase_options(self) -> None:
        """
        задание пользователем кастомных (пользовательских) параметров генерируемой парольной фразы
        """
        # перед вводом новых пользовательских параметров парольно фразы отображаем текущие
        self.show_passphrase_options('custom')

        # количество слов, из которых будет состоять парольная фраза
        tmp_defaults = self.CMD_OPTIONS_DEFAULTS["words_count"]
        print(f'\nPlease, enter the number of words to be used in the passphrase [{tmp_defaults["min_val"]}..{tmp_defaults["max_val"]}, default = {tmp_defaults["default"]}]: ',
              end='')
        words_count = input()
        # количество первых букв каждого слова парольно йрфазы, которые будут использоваться в парольной фразе при смене язывка
        tmp_defaults = self.CMD_OPTIONS_DEFAULTS["char_count"]
        print(f'Please, enter the number of first letters of each word to be used in the passphrase [{tmp_defaults["min_val"]}..{tmp_defaults["max_val"]}, default = {tmp_defaults["default"]}]: ',
              end='')
        char_count = input()
        # использовать ли цифры в парольной фразе
        print('Would you like to use numbers as part of the passphrase (yes[default]/no)? -> ', end='')
        use_numbers = input()
        # использовать ли специальные символы в парольной фразе
        print('Would you like to use special characters as part of the passphrase (yes/no[default])? -> ', end='')
        use_special = input()
        # использовать ли заглавные буквы в парольной фразе
        print('Would you like to use capital letters as part of the passphrase (yes/no[default])? -> ', end='')
        use_upper = input()

        # формируем словарь с введенными пользователем значениями параметров парольной фразы и обновляем их
        options = {
            'words_count': words_count,
            'char_count': char_count,
            'use_numbers': use_numbers,
            'use_special': use_special,
            'use_upper_case': use_upper
        }
        self.__update_custom_passphrase_options(options=options, is_upd_file=True)
    
    def __update_custom_passphrase_options(self, options:dict, is_upd_file:bool=False) -> None:
        """
        Обновление пользовательских параметров парольной фразы для их дальнейшего использования при генерации паролей с предварительным
        вызовом проверок применяемых параметров.
        Параметры могут быть введены пользователем вручную или считываться из конфигурационного файла. Проверки параметров
        осуществляются в любом случае.
        :param options: параметры, которые должны быть применены
        :param is_upd_file: флаг необходимости осуществить перезапись конфигурационного файла (true - перезаписат, false - нет)
        :return: None
        """
        # обновляем пользовательские (кастомные) параметры парольной фразы
        # каждое введенное пользователем или полученное из конфигурационного файла значение валидируется по заданным параметрам
        # если какое-либо значение не удовлетворяет заданным условиям, то оно принимает значене по умолчания для данного параметра
        try:
            self.__PASSPHRASE_PRESETS["custom"] = {
                # 'words_count': self.__check_custom_int_option(option=options["words_count"], default=4, min_val=2, max_val=6),
                # 'char_count': self.__check_custom_int_option(option=options["char_count"], default=3, min_val=3, max_val=5),
                # 'use_numbers': self.__check_custom_bool_option(option=options["use_numbers"], default=True),
                # 'use_special': self.__check_custom_bool_option(option=options["use_special"], default=False),
                # 'use_upper_case': self.__check_custom_bool_option(option=options["use_upper_case"], default=False)

                'words_count': self.__check_custom_int_option(option_name='words_count',
                                                              option=options["words_count"],
                                                              default=self.CMD_OPTIONS_DEFAULTS["words_count"]["default"],
                                                              min_val=self.CMD_OPTIONS_DEFAULTS["words_count"]["min_val"],
                                                              max_val=self.CMD_OPTIONS_DEFAULTS["words_count"]["max_val"]),
                'char_count': self.__check_custom_int_option(option_name='char_count',
                                                             option=options["char_count"],
                                                             default=self.CMD_OPTIONS_DEFAULTS["char_count"]["default"],
                                                             min_val=self.CMD_OPTIONS_DEFAULTS["char_count"]["min_val"],
                                                             max_val=self.CMD_OPTIONS_DEFAULTS["char_count"]["max_val"]),
                'use_numbers': self.__check_custom_bool_option(option_name='use_numbers',
                                                               option=options["use_numbers"],
                                                               default=True),
                'use_special': self.__check_custom_bool_option(option_name='use_special',
                                                               option=options["use_special"],
                                                               default=self.CMD_OPTIONS_DEFAULTS["use_special"]["default"]),
                'use_upper_case': self.__check_custom_bool_option(option_name='use_upper_case',
                                                                  option=options["use_upper_case"],
                                                                  default=self.CMD_OPTIONS_DEFAULTS["use_upper_case"]["default"])
            }
        except Exception as err:
            # обработка исключения - не найден ключ в словаре options; все пользовательские параметры сбрасываются к значениям по умолчанию
            logger_lib.error('Update custom passphrase options', f'Parameter {err} not found (probably, in configuration file). Default parameters will be used')
            self.set_defaults_options()
        
        # при необходимости записываем изменения в конфигурационный файл для последующего использования
        if is_upd_file:
            self.set_options(self.__PASSPHRASE_PRESETS["custom"])
    
    def __check_custom_int_option(self, option_name:str, option:str, default:int, min_val:int, max_val:int) -> int:
        """
        Метод валидации и определения целочисленных параметров пользовательской (кастомной) парольной фразы.
        Введенное пользователем значение прооверяется:
        1. Должно быть целым числом (содержать только цифры)
        2. Должно входить в допустимый диапазон значения параметра
        Если не выполняется любое из этих условий, то параметр парольной фразы принимает значение по умолчанию
        :param option_name: наименование параметра парольной фразы, который введен пользователем
        :param option: параметр парольной фразы, который введен пользователем
        :param default: значение параметра по умолчанию
        :param min_val: минимальное значение допустимого диапазона параметра
        :param max_val: максимальное значение допустимого диапазона параметра
        :return: целочисленное значение, которое примет параметр парольной фразы
        """
        # if match(r'^[0-9]+$', char_count) is None or int(char_count) not in range(3, 6):
        #     char_count = 3

        if match(r'^[0-9]+$', option) is None or int(option) not in range(min_val, max_val+1):
            logger_lib.warning(f'Update parameter \'{option_name}\'', f'Invalid parameter value; default value is used')
            return default
        else:
            return int(option)

    def __check_custom_bool_option(self, option_name:str, option:str, default:bool=True) -> bool:
        """
        Метод валидации и определения булевых параметров пользовательской (кастомной) парольной фразы
        Проверка и определение конечного значения проводится в два этапа:
        1. Введенное пользователм значение проверяется на вхождение в списки yes_ans и no_ans, результат объединаятся логической операцией xor.
        Так как операция xor =true в случае нечетного количества опреандов со значением true, то первая проверка определяет явно
        указанные пользователем положительный/отрицательный ответ. В случае результата провеки =false (ничего не введено или
        ввдено любое некооректное значение), то пераметр определяется как значение по умолчанию
        2. В случае =true первой проверки, определяется значение параметра парольной фразы исходя из вхождения в списки yes_ans
        :param option_name: наименование параметра парольной фразы, который введен пользователем
        :param option: параметр парольной фразы, который введен пользователем. Ожидается, что параметр принимает значения из списков yes_ans или no_ans.
            Все прочие значения будут инетрпритироваться как значения по умолчанию 
        :param default: булево значение параметра по умолчанию для параметра парольной фразы
        :return: булево значение, которое примет параметр парольной фразы исходя из пользовательского ответа
        """
        # region Const
        YES_NAS = ['', 'y', 'Y', 'yes', 'Yes', 'YES', 'True']
        NO_ANS = ['', 'n', 'N', 'no', 'No', 'NO', 'False']
        # endregion
        
        # if (use_upper in yes_ans) != (use_upper in no_ans):
        #     is_upper = True if use_upper in yes_ans else False
        # else:
        #     is_upper = True

        if (option in YES_NAS) != (option in NO_ANS):
            return True if option in YES_NAS else False
        else:
            logger_lib.warning(f'Update parameter \'{option_name}\'', f'Invalid parameter value; default value is used')
            return default
