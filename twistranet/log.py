"""
A simple logging facility
"""
import logging
from django.conf import settings

__all__ = ["log", ]

# create logger
log = logging.getLogger("twistranet")
log.setLevel(settings.TWISTRANET_LOG_LEVEL)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter("%(asctime)s - %(module)s:%(lineno)s:%(message)s")

# add formatter to ch
ch.setFormatter(formatter)

# add ch to log
log.addHandler(ch)
