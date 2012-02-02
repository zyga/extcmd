# Copyright (c) 2010, 2011 Linaro
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
A convenience wrapper around subprocess.Popen that allows the caller to
easily observe all stdout/stderr activity in real time. 
"""

__version__ = (1, 0, 0, "beta", 1)

from Queue import Queue
import subprocess
import sys
import threading
try:
    import posix
except ImportError:
    posix = None


class ExternalCommand(object):
    """
    A subprocess.Popen wrapper with that is friendly for sub-classing with
    common .call() and check_call() methods.
    """

    def call(self, *args, **kwargs):
        """
        Invoke a sub-command and wait for it to finish.
        """
        proc = self._popen(*args, **kwargs)
        proc.wait()
        return proc.returncode

    def check_call(self, *args, **kwargs):
        """
        Invoke a sub-command and wait for it to finish while raising exception
        if the return code is not zero.

        The raised exception is the same as raised by subprocess.check_call(),
        that is :class:`subprocess.CalledProcessError`
        """
        returncode = self.call(*args, **kwargs)
        if returncode != 0:
            raise subprocess.CalledProcessError(
                returncode, kwargs.get("args") or args[0])
        return returncode

    def _popen(self, *args, **kwargs):
        if posix:
            kwargs['close_fds'] = True
        return subprocess.Popen(*args, **kwargs)


class ExternalCommandWithDelegate(ExternalCommand):
    """
    The actually interesting subclass of ExternalCommand..
    
    Here both stdout and stderr are unconditionally captured and parsed for
    line-by-line output that is then passed to a helper delegate object.

    This allows writing 'tee' like programs that both display (with possible
    transformations) and store the output stream.

    ..note:
        Technically this class uses threads and queues to communicate which is
        very heavyweight but (yay) works portably for windows. A unix-specific
        subclass implementing this with _just_ poll could be provided with the
        same interface.

    """

    def __init__(self, delegate):
        """
        Set the delegate helper. Technically it needs to have a 'on_line()'
        method. For actual example code look at :class:`Tee`.
        """
        self._queue = Queue()
        self._delegate = delegate

    def call(self, *args, **kwargs):
        """
        Invoke the desired sub-process and intercept the output.
        See the description of the class for details.

        .. note:
            A very important aspect is that CTRL-C (aka KeyboardInterrupt) will
            KILL the invoked subprocess. This is handled by
            _on_keyboard_interrupt() method.
        """
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE
        proc = self._popen(*args, **kwargs)
        stdout_reader = threading.Thread(
            target=self._read_stream,
            args=(proc.stdout, "stdout"))
        stderr_reader = threading.Thread(
            target=self._read_stream,
            args=(proc.stderr, "stderr"))
        queue_worker = threading.Thread(
            target=self._drain_queue)

        queue_worker.start()
        stdout_reader.start()
        stderr_reader.start()
        try:
            proc.wait()
        except KeyboardInterrupt:
            self._on_keyboard_interrupt(proc)
        finally:
            stdout_reader.join()
            stderr_reader.join()
            self._queue.put(None)
            queue_worker.join()
        return proc.returncode

    def _on_keyboard_interrupt(self, proc):
        proc.kill()

    def _read_stream(self, stream, stream_name):
        for line in iter(stream.readline, ''):
            cmd = (stream_name, line)
            self._queue.put(cmd)

    def _drain_queue(self):
        while True:
            args = self._queue.get()
            if args is None:
                break
            self._delegate.on_line(*args)


class Chain(object):
    """
    Simple chaining output handler.
    """

    def __init__(self, delegate_list):
        self.delegate_list = delegate_list

    def on_line(self, stream_name, line):
        """
        Call the on_line() method on each delegate in the list
        """
        for delegate in self.delegate_list:
            delegate.on_line(stream_name, line)


class Redirect(object):
    """
    Redirect each line to desired stream.
    """

    def __init__(self, stdout=None, stderr=None):
        """
        Set stdout and stderr streams for writing the output to.
        If left blank then sys.stdout and sys.stderr are used instead.
        """
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

    def on_line(self, stream_name, line):
        """
        Write each line, verbatim, to the desired stream.
        """
        assert stream_name == 'stdout' or stream_name == 'stderr'
        if stream_name == 'stdout':
            self.stdout.write(line)
        else:
            self.stderr.write(line)


class Transform(object):
    """
    Transformation fiter

    Allows to transform each line before being passed down to subsequent
    delegate.
    """

    def __init__(self, callback, delegate):
        """
        Set the callback and subsequent delegate.
        """
        self.callback = callback
        self.delegate = delegate

    def on_line(self, stream_name, line):
        """
        Transform each line by calling callback(stream_name, line) and pass it
        down to the subsequent delegate.
        """
        transformed_line = self.callback(stream_name, line)
        self.delegate.on_line(stream_name, transformed_line)
