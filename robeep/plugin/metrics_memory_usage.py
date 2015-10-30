try:
    from robeep.packages import psutil
except ImportError:
    psutil = None

import logging
import os

_logger = logging.getLogger(__name__)


class MetricsMemoryUsage(object):
    """
    B2Bex2 [0] ~ $ free
    total       used       free     shared    buffers     cached
    Mem:          1932       1184        747          0         73        437
    -/+ buffers/cache:        674       1258
    Swap:            0          0          0
    """
    def __call__(self):
        if psutil is not None:
            mem = psutil.virtual_memory()
            return {
                'total': mem.total,
                'available': mem.available,
                'used': mem.used,
                'active': mem.active,
                'inactive': mem.inactive,
                'free': mem.free,
            }
        else:
            total, used, free = os.popen("free").readlines()[1].split()[1:4]
            return {
                'total': long(total),
                'used': long(used),
                'free': long(free)
            }


metrics_memory_usage = MetricsMemoryUsage
