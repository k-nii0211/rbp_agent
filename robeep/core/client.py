import logging

from robeep.packages import influxdb
from robeep.packages.influxdb.exceptions import InfluxDBClientError
from robeep.packages.requests.exceptions import ConnectionError

_logger = logging.getLogger(__name__)

USER_AGENT = 'Robeep Agent'


class Client(object):

    def __init__(self, auth_key=None, host='localhost', port=8086,
                 username=None, password=None, database='robeep',
                 ssl=False, verify_ssl=False, timeout=30.0):
        self._auth_key = auth_key
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._database = database
        self._timeout = timeout
        self._verify_ssl = verify_ssl

        self._client = influxdb.InfluxDBClient(host=host,
                                               port=port,
                                               username=username,
                                               password=password,
                                               database=database,
                                               ssl=ssl, verify_ssl=verify_ssl)

    def send_metrics(self, points, tags):
        try:
            self._client.write_points(points=points, tags=tags)
        except ConnectionError as e:
            _logger.exception("connection refused %r" % e)
        except InfluxDBClientError as e:
            _logger.exception("%r" % e)
