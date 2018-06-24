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
# thread for receiving a given file on given host and port over TCP
#

import sys
import socket
from threading import Thread

from settings import FILE_PKT_SIZE, FILE_RECV_PORT

# getting an instance of singleton logger
from logger import get_logger
log = get_logger()


class FileReceiver(Thread):

    def __init__(self, host, port, fname):
        super(FileReceiver, self).__init__()

        self.host = host
        self.port = port
        self.fname = fname

    def run(self):

        # binding socket on given host/ip and port
        server_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_skt.bind((self.host, self.port))

        # listening for sender to connect
        server_skt.listen(10)
        log.debug("Waiting for file sender...")

        skt, addr = server_skt.accept()
        log.debug("File sender connected")

        # reading file
        f = open(self.fname, "wb")
        data = skt.recv(FILE_PKT_SIZE)

        # sending file data in chunks of FILE_PKT_SIZE size
        while data:
            f.write(data)
            data = skt.recv(FILE_PKT_SIZE)

        # cleanup
        skt.close()

        log.info("File '%s' received successfully" % self.fname)

if __name__ == '__main__':
    # quick test for receiving an image file
    host = '192.168.1.2'
    port = FILE_RECV_PORT
    fname = "d.jpg"

    # initializing and staritng the file receiver thread
    f_recevier = FileReceiver(host, port, fname)
    f_recevier.start()

    # waiting for receiver thread to finish
    f_recevier.join()
