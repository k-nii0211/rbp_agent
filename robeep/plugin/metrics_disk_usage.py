from robeep.packages import psutil


class MetricsDiskUsage(object):
    def __init__(self, ignore_list=list()):
        self._ignore_list = ignore_list

    def __call__(self):
        total = 0
        used = 0
        free = 0
        for partition in psutil.disk_partitions():
            mountpoint = partition.mountpoint
            usage = psutil.disk_usage(mountpoint)
            total += usage.total
            used += usage.used
            free += usage.free

        return {
            'total': total,
            'used': used,
            'free': free,
        }


metrics_disk_usage = MetricsDiskUsage
