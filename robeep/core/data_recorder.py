import logging
import time
import threading

_logger = logging.getLogger(__name__)


class DataRecorder(object):
    def __init__(self, source, name, **settings):
        self._instance = source()
        self._name = ''.join(name.split())
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

    def pop_record_data(self):
        with self._record_data_lock:
            values = list(self._record_data)
            self._record_data = []
        return values

    def start(self):
        _logger.info('Starting data source (%s)' % self._name)
        self._start_timer()

    def _record(self):
        values = []
        start_time = time.time()
        if self._instance is not None:
            values = self._instance()
        elapsed_time = time.time() - start_time
        record_data = {
            'time': start_time,
            'values': values,
        }
        interval = self._interval - elapsed_time
        self._start_timer(interval)

        with self._record_data_lock:
            self._record_data.append(record_data)

    def _start_timer(self, interval=None):
        if interval is None:
            interval = self._interval
        if interval < 0:
            interval = 0

        timer = threading.Timer(interval, self._record, ())
        timer.setName('DataRecorder:%s' % self.name)
        timer.start()
