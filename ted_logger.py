# Copyright (c) 2020 Ted Miller. All rights reserved.

# Logging support. We create our own logger root so that we can configure only our own components
# while leaving logging from other components alone.
#
#   root.ted.xxx, root.ted.yyy, ... -> our loggers
#   root.xxx, root.yyy, ...         -> other loggers, which we don't want to configure

import logging
import time

_PREFIX = "ted"
_LEVEL = logging.DEBUG

# This exists solely to inject some logic into a late stage of logging so we can e.g.
# change the logger name.
class _Filter:
    def filter(self, record):
        s = record.name.split('.')
        if (len(s) > 0) and (s[0] == _PREFIX):
            record.name = ".".join(s[1:])
        return True

_console_handler = logging.StreamHandler()
_console_handler.setLevel(_LEVEL)
_console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
_console_handler.addFilter(_Filter())
_my_root_logger = logging.root.getChild(_PREFIX)
_my_root_logger.setLevel(_LEVEL)
_my_root_logger.addHandler(_console_handler)

# Change comma to dot for milliseconds, and use UTC for timestamp, globally (not just for ourselves).
logging.Formatter.default_msec_format = "%s.%03d"
logging.Formatter.converter = time.gmtime

def get_logger(name: str):
    """
    Gets a logger with the specified name.
    """
    return _my_root_logger.getChild(name)


