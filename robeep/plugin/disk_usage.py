import subprocess


class DiskUsageMetrics(object):
    def __call__(self):
        p = subprocess.Popen(['df', '-Pk'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        lines = stdout.splitlines()[1:]

        values = {}
        for line in lines:
            element = line.split()
            mount = element[-1]
            used_percentage = element[-2].strip('%')
            available = element[-3]
            used = element[-4]
            values[mount] = {
                'used': used,
                'available': available,
                'used_p': used_percentage,
            }
        return values


disk_usage_metrics = DiskUsageMetrics
