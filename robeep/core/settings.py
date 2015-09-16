import logging
import ConfigParser
from importlib import import_module

import robeep.core.logger
import robeep.core.exceptions
import robeep.core.agent

__all__ = ['initialize', 'setup_data_source']

_logger = logging.getLogger(__name__)

_config = ConfigParser.SafeConfigParser()


def _log_level_mapper(level):
    log_level = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
    }
    return log_level[level.upper()]


_data_sources = []


def _load_data_sources():
    agent_config = dict(_config.items('robeep'))
    if agent_config in 'interval':
        default_interval = agent_config['interval']
    else:
        default_interval = 60

    for section in _config.sections():
        if not section.startswith('data_source:'):
            continue

        try:
            name = _config.get(section, 'name')
            function = _config.get(section, 'function')
            (module, object_path) = function.split(':', 1)

            if _config.has_option(section, 'interval') is False:
                _config.set(section, 'interval', default_interval)

            settings = {}
            settings.update(_config.items(section))

            settings.pop('name', None)
            settings.pop('function', None)

            _data_sources.append(
                (section, module, object_path, name, settings))
        except Exception as e:
            _logger.exception('Attempt to load data source. %r' % e)


def _register_data_sources():
    agent = robeep.core.agent.get_instance()
    for section, module, object_path, name, settings in _data_sources:
        try:
            source = getattr(import_module(module), object_path)
            agent.register_data_source(source, name, **settings)
        except Exception as e:
            _logger.exception('Attempted to register data source %r' % e)


def initialize(config_file=None):
    if config_file is None:
        raise robeep.core.exceptions.ConfigurationError(
            'No configuration file.')

    if not _config.read([config_file]):
        raise robeep.core.exceptions.ConfigurationError(
            'Unable to read config file %s' % config_file)

    robeep_config = dict(_config.items('robeep'))
    log_file = robeep_config['log_file']
    log_level = _log_level_mapper(robeep_config['log_level'])
    robeep.core.logger.initialize(log_file, log_level)

    _logger.debug('Agent configuration file was %s' % config_file)


def setup_data_source():
    _load_data_sources()
    _register_data_sources()
