# region Import
from os import path
from re import split
# endregion


# region Params
DIR_BASE = '/'.join(split(r'[\\/]', path.abspath(__file__))[:-1])
DIR_DICTIONARIES = DIR_BASE + '/_dictionaries'
CONFIG = 'conf.ini'
# endregion


def main():
    from _libraries.argument_parser_lib import ArgumentParser

    argp = ArgumentParser(DIR_DICTIONARIES, CONFIG)
    argp.parse_arguments()
    del argp


if __name__ in '__main__':
    main()
