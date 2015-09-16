import logging
import time
import threading

_logger = logging.getLogger(__name__)


class DataSourceWrapper(object):
    def __init__(self, source, name, **settings):
        self._instance = source()
        self._name = name
        self._settings = dict(settings)
        self._interval = int(self._settings['interval'])
        self._record_data = []
        self._record_data_lock = threading.Lock()

        if self._instance is None:
            _logger.warning('Failed to create instance of data source %r'
                            % self._name)

    @property
    def name(self):
        return self._name

    @property
    def record_data(self):
        with self._record_data_lock:
            values = list(self._record_data)
            self._record_data = []
        return values

    def start(self):
        _logger.info('Starting data source (%s)' % self._name)
        threading.Timer(self._interval, self._record, ()).start()

    def _record(self):
        record_data = {
            'time': time.time(),
            'values': self._instance()
        }
        threading.Timer(self._interval, self._record, ()).start()

        with self._record_data_lock:
            self._record_data.append(record_data)
