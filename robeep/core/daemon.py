from __future__ import print_function

import sys
import os
import time
import atexit
import logging
import signal

import robeep.core.settings
import robeep.core.agent

_logger = logging.getLogger(__name__)

class Daemon(object):

    def __init__(self, pidfile):
        self.pidfile = pidfile
        robeep.core.settings.initialize(
            os.environ.get('ROBEEP_AGENT_CONFIG_FILE', None))

    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            _logger.exception('Failed to fork %r' % e)
            sys.exit(1)

        os.chdir('/')
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            _logger.exception('Failed to fork %r' % e)
            sys.exit(1)

        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        atexit.register(self.delete_pid)

        pid = str(os.getpid())
        with open(self.pidfile, 'w+') as f:
            f.write(pid + '\n')

    def delete_pid(self):
        os.remove(self.pidfile)

    def start(self):
        # Check for a pidfile to see if the daemon already runs
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if pid:
            _logger.error('Pidfile %s already exist.'
                          ' Daemon already running?' % self.pidfile)
            sys.exit(1)

        self.daemonize()
        robeep.core.settings.setup_data_source()
        robeep.core.agent.activate()

    def stop(self):
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if not pid:
            _logger.error('Pidfile %s does not exist.'
                          ' Daemon not running?' % self.pidfile)
            return

        try:
            while 1:
                # robeep.core.agent.shutdown()
                os.kill(pid, signal.SIGTERM)
                time.sleep(3)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                _logger.exception('%r' % err)
                sys.exit(1)

    def restart(self):
        self.stop()
        self.start()
