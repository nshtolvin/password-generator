# region Import
from contextlib import closing

from _libraries import logger_lib
# endregion


class DictFileWorker():
    # default constructor
    def __init__(self) -> None:
        pass
    
    def _read_dict_file(self, filename:str) -> list:
        """
        Считывание текстового файла в список строк (сериализация). Файл сичтывает полностью.
        :param filename: файл (имя файла и путь к нему), из которого считываются данные
        :return: список строк, содержащихся в текстовом файле. Важно: каждый элемент списка - строка, содержащая на конце символ \n
        """
        try:
            with closing(open(filename, "r")) as text_file:
                return text_file.readlines()
        except Exception as err:
            logger_lib.error(filename, err)
