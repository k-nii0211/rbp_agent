version = '0.1'

try:
    from robeep.build import build_number
except ImportError:
    build_number = 0

version_info = map(int, version.split('.')) + [build_number]
version = '.'.join(map(str, version_info))
