import logging
import time
import datetime
import threading

_logger = logging.getLogger(__name__)


class DataCollector(object):
    def __init__(self, source, name, **settings):
        self._instance = source()
        self._name = ''.join(name.split())
        self._settings = dict(settings)
        self._interval = int(self._settings['interval'])
        self._record_data = []
        self._record_data_lock = threading.Lock()
        self._record_shutdown = threading.Event()

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
        _logger.debug('Starting data source (%s)' % self._name)
        self._start_timer()

    def stop(self):
        self._record_shutdown.set()

    def _record(self):
        values = []
        start_time = time.time()

        if self._instance is not None:
            values = self._instance()
        now = "%sZ" % datetime.datetime.utcnow().isoformat()

        elapsed_time = time.time() - start_time
        _logger.debug('collect %s took %f ms' % (self._name, elapsed_time*1000))

        interval = self._interval - elapsed_time
        if interval < 0:
            _logger.warn('collect %s took %f ms' %
                         (self._name, elapsed_time*1000))

        self._start_timer(interval)

        record_data = {
            'time': now,
            'record': values,
        }
        with self._record_data_lock:
            self._record_data.append(record_data)

    def _start_timer(self, interval=None):
        if self._record_shutdown.isSet():
            _logger.debug('%s collector shutdown' % self._name)
            return

        if interval is None:
            interval = self._interval
        if interval < 0:
            interval = 0

        timer = threading.Timer(interval, self._record, ())
        timer.setName('DataRecorder:%s' % self.name)
        timer.start()
