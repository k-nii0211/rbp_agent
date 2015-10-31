import logging

_logger = logging.getLogger(__name__)

try:
    from naoqi import ALProxy
except ImportError, e:
    ALProxy = None

_keys = [
    "Head",
    "Battery",
    "HeadYaw",
    "HeadPitch",
    "LElbowYaw",
    "LElbowRoll",
    "RElbowYaw",
    "RElbowRoll",
    "LHand",
    "LWristYaw",
    "RHand",
    "RWristYaw",
    "LShoulderPitch",
    "LShoulderRoll",
    "RShoulderPitch",
    "RShoulderRoll",
    "HipRoll",
    "HipPitch",
    "KneePitch",
    "WheelFL",
    "WheelFR",
    "WheelB"
]


class MetricsDeviceTemperature(object):
    def __call__(self):
        if ALProxy is None:
            _logger.warn('ALProxy is None.')
            return None

        memProxy = ALProxy("ALMemory", "localhost", 9559)
        ret = dict()
        for key in _keys:
            value = memProxy.getData(
                "Device/SubDeviceList/%s/Temperature/Sensor/Value" % key)
            ret[key] = value
            if not value:
                _logger.warn('Noting return value %s' % key)
                continue
        return ret

metrics_device_temperature = MetricsDeviceTemperature
