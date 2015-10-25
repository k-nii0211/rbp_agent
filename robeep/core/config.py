__all__ = ['global_config']


class _Config(object):
    def __repr__(self):
        return repr(self.__dict__)


class RobeepConfig(_Config):
    pass


_config = _Config()
_config.robeep = dict()
_config.robeep['name'] = 'robeep agent'
_config.robeep['host'] = 'localhost'
_config.robeep['port'] = 8086
_config.robeep['username'] = None
_config.robeep['password'] = None
_config.robeep['database'] = 'robeep'
_config.robeep['ssl'] = False
_config.robeep['verify_ssl'] = False
_config.robeep['timeout'] = 30.0
_config.robeep['environment'] = 'product'


def global_config():
    return _config
