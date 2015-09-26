import logging
import json
import time

from .exceptions import DiscardDataException

from ..packages import requests

_logger = logging.getLogger(__name__)

USER_AGENT = 'Robeep Agent'


class Client(object):

    def __init__(self, auth_key=None, host='localhost.local', port=8080,
                 ssl=True, timeout=30.0):
        self._auth_key = auth_key
        self._host = host
        self._port = port
        self._timeout = timeout
        self._session = None
        self._proxies = None

        self._scheme = "http"
        if ssl:
            self._scheme = "https"

        self._base_url = "{0}://{1}:{2}".format(self._scheme,
                                                self._host,
                                                self._port)

    def send_request(self, path, method='POST', params=None, payload=(),
                     timeout=None):

        start = time.time()

        header = {
            'UserAgent': USER_AGENT,
            'Content-Encoding': 'identity',
            'X-Auth-Key': self._auth_key,
            'X-Marshal-Format': 'json',
        }

        try:
            data = json.dumps(payload)
        except Exception as e:
            _logger.exception('Error encoding data for JSON payload with data '
                              'of %r. Exception which occurred was %r. ',
                              payload, e)

            raise DiscardDataException(str(e))

        _logger.debug('Calling data collector to report custom metrics '
                      'with payload=%r.', data)

        if timeout is None:
            timeout = self._timeout

        if self._session is None:
            self._session = requests.session()

        url = "%s/%s" % (self._base_url, path)
        try:
            res = self._session.request(url, method=method, header=header,
                                        params=params, data=data,
                                        timeout=timeout)
            content = res.content
        except Exception as e:
            _logger.exception('error raised was %r.' % e)
            raise e

        if res.staus_code > 200:
            _logger.debug('')
            raise Exception

        duration = time.time() - start
        _logger.debug('valid response from collector after %f seconds'
                      ' with content: %r' % (duration, content))
        # result = json.

        if res.status_code == 200:
            return content

        raise DiscardDataException
