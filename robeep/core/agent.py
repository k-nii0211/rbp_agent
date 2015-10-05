import logging
import threading
import time
import atexit

from robeep.core.data_collector import DataCollector
from robeep.core.client import Client
import robeep.core.config
from robeep.core.exceptions import ConfigurationError

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

        global_config = robeep.core.config.global_config()
        with Agent._instance_lock:
            instance = Agent(global_config)
            Agent._instance = instance
        return instance

    def __init__(self, global_config):
        self._data_collector_thread = threading.Thread(
            target=self.data_collector, name='DataCollectorThread')
        self._data_collector_thread.setDaemon(True)
        self._collector_shutdown = threading.Event()
        self._active = False
        self._next_collect = 0.0
        self._global_config = global_config

        robeep_config = self._global_config.robeep

        self._client = Client(
            host=robeep_config['host'],
            port=robeep_config['port'],
            username=robeep_config['username'],
            password=robeep_config['password'],
            database=robeep_config['database'],
            ssl=robeep_config['ssl'],
            verify_ssl=robeep_config['verify_ssl'],
        )

        self._hostname = robeep_config['hostname']
        if self._hostname is None:
            raise ConfigurationError('hostname is must be set.')

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
                        record_data = data_source.pop_record_data()
                        if not record_data:
                            _logger.debug('%s record is empty.' %
                                          data_source.name)
                            continue

                        start_time = time.time()
                        self._client.send_metrics(points=[
                            {
                                'measurement': data_source.name,
                                'time': d['time'],
                                'fields': _make_fields(d['record']),
                            } for d in record_data
                        ], tags=self._make_tags())
                        elapsed_time = time.time() - start_time
                        _logger.debug('send %s took %f ms' % (
                                      data_source.name, elapsed_time*1000))
        except Exception as e:
            _logger.exception('Unexpected exception in collector loop %r' % e)

    def _make_tags(self):
        return {'host': self._hostname}


def _make_fields(data):
    return {"value_%s" % key: value for key, value in data.iteritems()}


def get_instance():
    return Agent.get_instance()


def activate():
    return Agent.get_instance().activate()


def shutdown():
    # FIXME:
    instance = Agent.get_instance()
    return instance.shutdown()
