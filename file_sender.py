#!/usr/bin/python3

"""
 PyLanMessenger
 ______________

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

 Project Author/Architect: Navjot Singh <weavebytes@gmail.com>

"""

#
# thread for sending a given file on given host and port over TCP
#

import sys
import socket
import os
from threading import Thread

from settings import FILE_PKT_SIZE, FILE_RECV_PORT

# getting an instance of singleton logger
from logger import get_logger
log = get_logger()


class FileSender(Thread):

    def __init__(self, host, port, fname):
        super(FileSender, self).__init__()

        self.host = host
        self.port = port
        self.fname = fname

    def run(self):
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.connect((self.host, self.port))

        total = os.path.getsize(self.fname)
        log.debug("total file size = %ld" % total)
        sent = 0

        f = open(self.fname, "rb")
        data = f.read(FILE_PKT_SIZE)
        sent += len(data)
        while data:
            skt.send(data)
            sent += len(data)
            log.debug("Sent: %ld" % sent)

            # data sent progress
            p = float(float(sent)/float(total)) * 100
            log.debug("percentage: %f" % p)
            data = f.read(FILE_PKT_SIZE)

        # cleanup
        skt.close()

        log.info("File '%s' sent successfully" % self.fname)

if __name__ == '__main__':
    # quick test for sending an image file
    fname = '/home/neo/Desktop/p.jpg'
    host = '192.168.1.2'
    port = FILE_RECV_PORT

    # initializing and staritng the file sender thread
    f_sender = FileSender(host, port, fname)
    f_sender.start()

    # waiting for sender thread to finish
    f_sender.join()
