import logging

_logger = logging.getLogger(__name__)

try:
    from naoqi import ALProxy
except ImportError, e:
    ALProxy = None

_keys = {
    "Head": "Device/SubDeviceList/Head/Temperature/Sensor/Value",
    "Battery": "Device/SubDeviceList/Battery/Temperature/Sensor/Value",
    "HeadYaw": "Device/SubDeviceList/HeadYaw/Temperature/Sensor/Value",
    "HeadPitch": "Device/SubDeviceList/HeadPitch/Temperature/Sensor/Value",
    "LElbowYaw": "Device/SubDeviceList/LElbowYaw/Temperature/Sensor/Value",
}


class MetricsDeviceTemperature(object):
    def __call__(self):
        if ALProxy is None:
            _logger.warn('')
            return None

        memProxy = ALProxy("ALMemory", "localhost", 9559)
        ret = dict()
        for key in _keys:
            ret[key] = memProxy.getData(key)
        return ret

metrics_device_temperature = MetricsDeviceTemperature
