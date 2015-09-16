import logging

from threading import Timer

_logger = logging.getLogger(__name__)


class DataSourceWrapper(object):
    def __init__(self, source, name, **settings):
        self._instance = source()
        self._name = name
        self._settings = dict(settings)
        self._interval = int(self._settings['interval'])

        if self._instance is None:
            _logger.warning('Failed to create instance of data source %r'
                            % self._name)

    @property
    def name(self):
        return self._name

    def start(self):
        _logger.info('Starting data source (%s)' % self._name)
        Timer(self._interval, self._metrics, ()).start()

    def _metrics(self):
        values = self._instance()
        _logger.info(values)
        Timer(self._interval, self._metrics, ()).start()
