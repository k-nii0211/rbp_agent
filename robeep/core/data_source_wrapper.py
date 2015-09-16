import logging

_logger = logging.getLogger(__name__)

class DataSourceWrapper(object):

    def __init__(self, source, name, **settings):
        self.instance = source()
        self.name = name
        self.settings = dict(settings)

        if self.instance is None:
            _logger.warning('Failed to create instance of data source %r'
                            % self.name)

    def metrics(self):
        if self.instance is None:
            return []
        _logger.warn(self.settings['interval'])
        return self.instance()
