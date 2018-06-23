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
# wrapper for database transactions
#

from models import Message, get_session


class Db:

    def __init__(self):
        self.session = get_session()

    def add_msg(
            self, sender_host, sender_ip, receiver_host, receiver_ip, body):
        m = Message(sender_host, sender_ip, receiver_host, receiver_ip, body)
        self.session.add(m)
        self.session.commit()

    def get_all_msgs(self):
        return self.session.query(Message).all()


def quick_tests():
    db = Db()
    db.add_msg(
            "Navi", "192.168.1.18", "Tom", "192.168.1.20", "Hello from navi")
    for msg in db.get_all_msgs():
        print(msg.to_dict())
        msg.log()

if __name__ == '__main__':
    quick_tests()
