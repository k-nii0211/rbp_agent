import logging
import threading
import time
import atexit

from .data_collector import DataCollector

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
        self._data_collector_thread.setDaemon(True)
        self._collector_shutdown = threading.Event()
        self._active = False
        self._next_collect = 0.0
        atexit.register(self._atexit_shutdown)

    def register_data_source(self, source, name=None, **settings):
        with self._data_source_lock:
            self._data_sources.append(
                DataCollector(source, name, **settings))
            _logger.debug('Register data source with agent %r.' %
                          ((source, name, settings),))

    def activate(self):
        if self._collector_shutdown.isSet():
            return
        if self._active:
            return
        if self._data_collector_thread.isAlive():
            _logger.warn('data collector thread is already alive.')
            return
        self._start_data_record()
        self._data_collector_thread.start()

    def _start_data_record(self):
        with self._data_source_lock:
            for data_source in self._data_sources:
                data_source.start()

    def _atexit_shutdown(self):
        self._active = False
        self.shutdown()

    def shutdown(self, timeout=5.0):
        if self._collector_shutdown.isSet():
            return

        self._collector_shutdown.set()
        self._data_collector_thread.join(timeout)
        _logger.info('Agent shutdown...')

    def data_collector(self):
        if self._active:
            return

        self._next_collect = time.time()
        try:
            while True:
                if self._collector_shutdown.isSet():
                    return

                now = time.time()
                while self._next_collect <= now:
                    self._next_collect += 60.0

                self._collector_shutdown.wait(self._next_collect - now)

                if self._collector_shutdown.isSet():
                    return

                with self._data_source_lock:
                    for data_source in self._data_sources:
                        _logger.info(data_source.pop_record_data())
        except Exception as e:
            _logger.exception('Unexpected exception in collector loop %r' % e)


def get_instance():
    return Agent.get_instance()


def activate():
    return Agent.get_instance().activate()


def shutdown():
    # FIXME:
    instance = Agent.get_instance()
    return instance.shutdown()
