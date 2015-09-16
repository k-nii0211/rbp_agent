import logging
import threading
import time

from robeep.core.data_source_wrapper import DataSourceWrapper

_logger = logging.getLogger(__name__)


class Agent(object):
    _instance = None
    _instance_lock = threading.Lock()

    _data_source_lock = threading.Lock()
    _data_sources = []

    @staticmethod
    def get_instance():
        # FIXME: must to be strict singleton model
        if Agent._instance is not None:
            return Agent._instance

        with Agent._instance_lock:
            instance = Agent()
            Agent._instance = instance
        return instance

    def __init__(self):
        self._data_collector_thread = threading.Thread(
            target=self.data_collector, name='DataCollectorThread')
        self._agent_shutdown = False
        self._active = False

    def register_data_source(self, source, name=None, **settings):
        with self._data_source_lock:
            self._data_sources.append(
                DataSourceWrapper(source, name, **settings))
        _logger.debug('Register data source with agent %r.' %
                      ((source, name, settings),))

    def activate(self):
        if self._agent_shutdown:
            return
        if self._active:
            return
        self._data_collector_thread.start()

    def shutdown(self):
        self._agent_shutdown = True

    def data_collector(self):
        if self._agent_shutdown:
            return
        if self._active:
            return

        while not self._agent_shutdown:
            _logger.debug('running...')
            with self._data_source_lock:
                for data_source in self._data_sources:
                    _logger.info(data_source.metrics())
            time.sleep(3)


def get_instance():
    return Agent.get_instance()


def activate():
    return Agent.get_instance().activate()


def shutdown():
    # FIXME:
    instance = Agent.get_instance()
    return instance.shutdown()
