# The MIT License (MIT)
#
# Copyright (c) 2019 ladyada for Adafruit Industries
# Modified by Brent Rubell for Adafruit Industries, 2020
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_wiznet5k_socket`
================================================================================

A socket compatible interface with the Wiznet5k module.

* Author(s): ladyada, Brent Rubell

"""
import gc
from micropython import const
from adafruit_wiznet5k import adafruit_wiznet5k

_the_interface = None   # pylint: disable=invalid-name
def set_interface(iface):
    """Helper to set the global internet interface"""
    global _the_interface   # pylint: disable=global-statement, invalid-name
    _the_interface = iface

SOCK_STREAM = const(1)
AF_INET = const(2)
NO_SOCKET_AVAIL = const(255)

MAX_PACKET = const(4000)

class socket:
    """A simplified implementation of the Python 'socket' class
    for connecting to a Wiznet5k module.

    """
    def __init__(self, family=AF_INET, type=SOCK_STREAM, proto=0, fileno=0, socknum=None):
        if family != AF_INET:
            raise RuntimeError("Only AF_INET family supported by W5K modules.")
        if type != SOCK_STREAM:
            raise RuntimeError("Only SOCK_STREAM type supported.")
        self._buffer = b''
        self._socknum = socknum if socknum else _the_interface.get_socket()
        # TODO: implement set_timeout
        # self.set_timeout(0)
    
    def connected(self):
        """Returns whether or not we are connected to the socket.
        """
        if (self._socknum >= _the_interface.max_sockets):
            return 0
        else:
            status = _the_interface.socket_status(self._socknum)
            result = status not in (adafruit_wiznet5k.SNSR_SOCK_CLOSED,
                                    adafruit_wiznet5k.SNSR_SOCK_LISTEN,
                                    adafruit_wiznet5k.SNSR_SOCK_CLOSE_WAIT,
                                    adafruit_wiznet5k.SNSR_SOCK_FIN_WAIT)
            if not result:
                self.close()
            return result

    def connect(self, address, conn_type=None):
        """Connect to a remote socket at address. (The format of address depends on the address family — see above.)
        """
        host, port = address

        if conn_type is None:
            conn_type = _the_interface.SNMR_TCP
        if not _the_interface.socket_connect(self._socknum, host, port, conn_mode=conn_type):
            raise RuntimeError("Failed to connect to host", host)
        self._buffer = b''
    
    def send(self, data):
        """Send data to the socket. The socket must be connected to
        a remote socket.
        Returns the number of bytes sent

        """
        _the_interface.socket_write(self._socknum, data)
        gc.collect()
    
    def close(self):
        """Closes the socket.
        """
        _the_interface.socket_close(self._socknum)