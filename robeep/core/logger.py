import sys
import logging
import threading

__all__ = ['initialize']

_lock = threading.Lock()

_logger = logging.getLogger('robeep')
_logger.addHandler(logging.NullHandler())

_LOG_FORMAT = '%(asctime)s (%(process)d/%(threadName)s) ' \
              '[%(levelname)s] %(name)s - %(message)s'


def initialize(log_file, log_level = logging.INFO):
    with _lock:
        handler = None
        if log_file == 'stdout':
            handler = logging.StreamHandler(sys.stdout)
        elif log_file == 'stderr':
            handler = logging.StreamHandler(sys.stderr)
        elif log_file:
            handler = logging.FileHandler(log_file)

        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        _logger.addHandler(handler)
        _logger.setLevel(log_level)
        _logger.debug('Initialize logger (level:%s, %s)' %
                      (log_level, log_file))
