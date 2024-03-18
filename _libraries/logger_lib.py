# region Import
import logging
# endregion


# region Logging
logging.basicConfig(format='%(asctime)s'
                           ' - %(name)s'
                           ' - %(levelname)s'
                           ' - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
# endregion


# Log Errors caused by Updates.
def error(update, msg):
    logger.error(f'Update "{update}" caused error "{msg}"')
    # print(update, "\n", msg)


def warning(update, msg):
    logger.warning(f'Update "{update}" caused warning "{msg}"')
    # print(update, "\n", msg)


def info(update, msg):
    logger.info(f'Update "{update}" info "{msg}"')
    # print(update, "\n", msg)
