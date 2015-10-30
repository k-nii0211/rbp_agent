import subprocess
import logging

_logger = logging.getLogger(__name__)


class CheckPing(object):
    def __init__(self, host='localhost'):
        self._host = host

    def __call__(self):
        return {'status': 0}
        # status = 1
        # cmd = '/sbin/ping -c 1 %s' % self._host
        # try:
        #     ping = subprocess.Popen(cmd,
        #                             shell=True,
        #                             stdout=subprocess.PIPE,
        #                             stderr=subprocess.PIPE)
        #     stdout, stderr = ping.communicate()
        #     if ping.returncode == 0:
        #         status = 0
        #     else:
        #         _logger.warn('communication error %r' % stderr)
        # except Exception as e:
        #     _logger.exception('%r', e)


check_ping = CheckPing
