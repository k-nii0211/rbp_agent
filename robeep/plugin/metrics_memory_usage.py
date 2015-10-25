from robeep.packages import psutil


class MetricsMemoryUsage(object):
    def __call__(self):
        mem = psutil.virtual_memory()

        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'active': mem.active,
            'inactive': mem.inactive,
            'free': mem.free,
        }

metrics_memory_usage = MetricsMemoryUsage
