import os


class MetricsLoadAverage(object):
    def __call__(self):
        values = os.getloadavg()
        return {'1m': round(values[0], 2),
                '5m': round(values[1], 2),
                '15m': round(values[2], 2),
                }


metrics_load_average = MetricsLoadAverage
