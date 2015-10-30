try:
    from robeep.packages import psutil
except ImportError:
    psutil = None

import os
from collections import namedtuple

disk_ntuple = namedtuple('partition',  'device mountpoint fstype')
usage_ntuple = namedtuple('usage',  'total used free percent')


def disk_partitions(all=False):
    """Return all mountd partitions as a nameduple.
    If all == False return phyisical partitions only.
    """
    phydevs = []
    f = open("/proc/filesystems", "r")
    for line in f:
        if not line.startswith("nodev"):
            phydevs.append(line.strip())

    retlist = []
    f = open('/etc/mtab', "r")
    for line in f:
        if not all and line.startswith('none'):
            continue
        fields = line.split()
        device = fields[0]
        mountpoint = fields[1]
        fstype = fields[2]
        if not all and fstype not in phydevs:
            continue
        if device == 'none':
            device = ''
        ntuple = disk_ntuple(device, mountpoint, fstype)
        retlist.append(ntuple)
    return retlist


def disk_usage(path):
    """Return disk usage associated with path."""
    st = os.statvfs(path)
    free = (st.f_bavail * st.f_frsize)
    total = (st.f_blocks * st.f_frsize)
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    try:
        percent = ret = (float(used) / total) * 100
    except ZeroDivisionError:
        percent = 0
    # NB: the percentage is -5% than what shown by df due to
    # reserved blocks that we are currently not considering:
    # http://goo.gl/sWGbH
    return usage_ntuple(total, used, free, round(percent, 1))


class MetricsDiskUsage(object):
    def __init__(self, ignore_list=list()):
        self._ignore_list = ignore_list

    def __call__(self):
        total = 0
        used = 0
        free = 0
        if psutil is not None:
            for partition in psutil.disk_partitions():
                mountpoint = partition.mountpoint
                usage = psutil.disk_usage(mountpoint)
                total += usage.total
                used += usage.used
                free += usage.free
        else:
            for part in disk_partitions():
                usage = disk_usage(part.mountpoint)
                total += usage.total
                used += usage.used
                free += usage.free
        return {
            'total': total,
            'used': used,
            'free': free,
        }


metrics_disk_usage = MetricsDiskUsage
