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
# a packetizer to compose JSON packets for different
# type of messages to be sent over nw

import json


class Packet:

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_json(self):
        return json.dumps(
                self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


if __name__ == '__main__':
    # testing "I Am In" packet
    print(Packet(op="IAI", ip="192.168.1.18", host="neo").to_json())

    # testing "Me Too In" packet
    print(Packet(op="MTI", ip="192.168.1.20", host="tom").to_json())

    # testing "Text Chat Message" packet
    print(Packet(
        op="TCM", ip="192.168.1.20", host="tom",
        msg="Hi neo, its Tom here!!!").to_json())
