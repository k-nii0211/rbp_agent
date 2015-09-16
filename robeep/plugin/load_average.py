import os
import logging
import subprocess

_logger = logging.getLogger(__name__)

class LoadAverageMetrics(object):
    def __call__(self):
        if os.path.exists("/proc/loadavg"):
            with open('/proc/loadavg') as load_avg:
                values = load_avg.read().strip().split(' ')[:3]
        else:
            p = subprocess.Popen(['uptime'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            values = stdout[3:].rsplit(':', 1)[1].strip().split(' ')[:3]
        return {'load_avg/1m': values[0],
                'load_avg/5m': values[1],
                'load_avg/15m': values[2],
                }

load_average_metrics = LoadAverageMetrics
