# Copyright (c) 2013 Vadim Rutkovsky <vrutkovs@redhat.com>
# Copyright (c) 2013 Guillaume Quintard <guillaume.quintard@gmail.com>
# Copyright (c) 2013 Eslam Mostafa <cseslam@gmail.com>
# Copyright (c) 2013 Manish Sinha <manishsinha@ubuntu.com>
#
# GNOME Music is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# GNOME Music is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with GNOME Music; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# The GNOME Music authors hereby grant permission for non-GPL compatible
# GStreamer plugins to be used and distributed together with GStreamer
# and GNOME Music.  This permission is above and beyond the permissions
# granted by the GPL license by which GNOME Music is covered.  If you
# modify this code, you may extend this exception to your version of the
# code, but you are not obligated to do so.  If you do not wish to do so,
# delete this exception statement from your version.

from gi.repository import Tracker
from itertools import chain
import logging
import time
logger = logging.getLogger(__name__)
tabbing = 0


def log(fn):
    if logger.getEffectiveLevel() > logging.DEBUG:
        return fn

    def wrapped(*v, **k):
        global tabbing
        name = fn.__name__
        module = fn.__module__
        params = ", ".join(map(repr, chain(v, k.values())))

        tabbing += 1
        start = time.time()
        retval = fn(*v, **k)
        elapsed = time.time() - start
        tabbing -= 1
        elapsed_time = ''
        if elapsed > 0.5:
            elapsed_time = ', took %02f' % elapsed
        logger.debug("%s%s.%s(%s), returned %s%s", '|' * tabbing, module, name, params, retval, elapsed_time)

        return retval
    return wrapped


def RateLimited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)

    def decorate(func):
        lastTimeCalled = [0.0]

        def rateLimitedFunction(*args, **kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait > 0:
                time.sleep(leftToWait)
            ret = func(*args, **kargs)
            lastTimeCalled[0] = time.clock()
            return ret

        return rateLimitedFunction

    return decorate


class TrackerWrapper:
    class __TrackerWrapper:
        def __init__(self):
            try:
                self.tracker = Tracker.SparqlConnection.get(None)
            except Exception as e:
                from sys import exit
                logger.error("Cannot connect to tracker, error '%s'\Exiting", str(e))
                exit(1)

        def __str__(self):
            return repr(self)
    instance = None

    def __init__(self):
        if not TrackerWrapper.instance:
            TrackerWrapper.instance = TrackerWrapper.__TrackerWrapper()

    def __getattr__(self, name):
        return getattr(self.instance, name)
