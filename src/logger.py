import codecs
import logging
import sys


def setup_std_handler(level):
    if sys.stdout.encoding != 'UTF-8':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

    if sys.stderr.encoding != 'UTF-8':
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

    logging.basicConfig(
        level=logging.getLevelName(level),
        format='%(asctime)s [%(levelname)s](%(name)s:%(funcName)s:%(lineno)d): %(message)s'
    )

