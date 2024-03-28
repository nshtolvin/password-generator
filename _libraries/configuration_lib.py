# region Import
from contextlib import closing
from configparser import ConfigParser
from os import path

from _libraries import logger_lib
# endregion


# Class for configuration
# класс предназначен для работы с файлом, содержащим паользовательские (кастомные) параметры парольной фразы
class Config():
    # default constructor
    def __init__(self, conf_filename:str, defaults:dict):
        self.__filename = conf_filename
        self.__config = ConfigParser()

        # сохраняем все параметры по умолчанию для пользовательского пароля (они же - кастомные параметры)
        # необходимо для отката к дефотным параметрам в случаях:
        # 1. Пользователь самостоятельно изменил значения в конфигурационном файле conf.ini на те, что не могут быть корректно обработан
        # 2. Пользователь запросил откат кастомных параметров пароля к дефолтным значения через меню утилиты
        # значения параметров для универсальности приводятся к типу string
        self.__defaults = dict()
        for key in defaults.keys():
            self.__defaults[key] = str(defaults[key])

        # при инициализации объекта класса паользовательские параметры парольной фразы могут быть
        # - приняты по умолчанию
        # - считаны из конфигурационнного файла
        
        # проверка существования файла conf.ini с пользовательскими параметрами парольной фразы
        # - если файл не найден, то он создается; параметры парольной фразы задаются значениями по умолчанию из defaults
        # - если файл существет, то секция пропускается
        if not path.exists(self.__filename):
            logger_lib.error(self.__filename, 'File not found')
            self.__create_config_file(defaults)
        
        # счиитываем кастомные параметры парольной фразы
        self.read_settings()
    
    # default destructor
    def __del__(self):
        del self.__config
    
    # read parameters from file
    def read_settings(self) -> None:
        try:
            self.__config.read(self.__filename)
        except Exception as err:
            logger_lib.error(self.__filename, err)

    # write parameters to file
    def write_settings(self) -> int:
        try:            
            # открытие файла на запись
            # если файл содержит какие-либо данные, то они будут перезаписаны
            # если файл не существует, то он будщет создан
            with closing(open(self.__filename, "w")) as ini_file:
                # запись параметров в указанный файл
                self.__config.write(ini_file)
                return 0
        except Exception as err:
            logger_lib.error(self.__filename, err)
            return -1

    def __create_config_file(self, options:dict) -> None:
        """
        Задание пользовательских (кастомных) параметров парольной фразы
        :param options: словарь с пользовательскими параметрами парольной фразы
        :return: None
        """
        # конфигурационный файл будет содержать кастомные параметры парольной фразы в секции passphrase
        self.__config.add_section('passphrase')
        # перебираем все пары ключ-значение параметров и заносим из в обект ConfigParser
        for key, value in options.items():
            self.__config.set('passphrase', key, str(value))
        # запись параметров в файл
        self.write_settings()
        logger_lib.info(self.__filename, 'file created')
    
    def get_options(self) -> dict:
        """
        Метод преобразования считанных из конфигурационного файла кастомных параметров парольной фразы в словарь
        :return: None
        """
        try:
            # словарь со считанными пользовательскими параметрами
            options = dict()
            for option in self.__config['passphrase']:
                options[option] = self.__config.get('passphrase', option)
            return options 
        except KeyError as err:
            # если в конфигурационном файле отсутствует секция passphrase с кастомными параметрами парольной фразы, то
            # все секции конфигурационного файла удалюятся, а на их место заносится одна секция passphrase с параметрами по умолчанию
            logger_lib.error('Get options', f'Section {err} not found. Default options will be used')
            self.set_defaults_options()
            return self.__defaults
    
    def set_options(self, options:dict) -> int:
        """
        Метод преобразования введенных пользователем кастомных параметров парольной фразы в поля объекта ConfigParser
        :param options: словарь с пользовательскими параметрами парольной фразы
        :return: 0 - данные успешно записаны в конфигурационный файл, -1 - в противном случае
        """
        # если в текщих пользовательских параметрах нет секции passphrase, то она добавляется
        if not self.__config.has_section('passphrase'):
            self.__config.add_section('passphrase')
        # добалвение всех параметров и их значений в секцию passphrase
        for key, value in options.items():
            self.__config.set('passphrase', key, str(value))
        # запись изменений в файл
        return self.write_settings()
    
    def set_defaults_options(self) -> int:
        """
        Сброс всех пользовательских параметров парольной фразы в значения по умолчанию. Метод применяется если:
        1. Не найдена секция passphrase в конфигурационном файле
        2. Название какого-либо из параметров секции passphrase изменено или параметр вовсе отсутсвует
        :return: 0 - параметры по умолчанию успешно записаны в конфигурационный файл, -1 - в противном случае
        """
        # удаление всех текущих секций
        for itm in self.__config.sections():
            self.__config.remove_section(itm)
        # добавление секции passphrase с параметрами по умолчанию
        return self.set_options(self.__defaults)
