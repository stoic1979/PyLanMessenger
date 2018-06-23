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
# script for defining various ORM models for project
#
# Note: we are using sqlite for local caching of
# the chat history/messages
#
import traceback
from sqlalchemy import Column, Integer, String, DateTime, Date
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

db = create_engine('sqlite:///data.db')

# disbale db warning
db.echo = False

base = declarative_base()


class Message(base):
    """
    model for storing information about each chat message
    """

    __tablename__ = 'message'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_host = Column(String(64))
    sender_ip = Column(String(32))
    receiver_host = Column(String(64))
    receiver_ip = Column(String(32))
    body = Column(String(1024))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(
            self, sender_host, sender_ip, receiver_host, receiver_ip, body):
        self.sender_host = sender_host
        self.sender_ip = sender_ip
        self.receiver_host = receiver_host
        self.receiver_ip = receiver_ip
        self.body = body

    def __repr__(self):
        return "<Message> %s to %s at %s" % (
                self.sender_host, self.receiver_host, self.created_date)

    def to_dict(self):
        """
        function for converting  Message model to python dictionary
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def log(self):
        """
        convenience function for logging message content
        """
        print("---------------[ MESSAGE ] --------------------")
        print(" Sender Host . . :", self.sender_host)
        print(" Sender IP . . . :", self.sender_ip)
        print(" Receiver Host . :", self.receiver_host)
        print(" Receiver IP . . :", self.receiver_ip)
        print(" Body . . . . .  :", self.body)
        print(" Timestamp . . . :", self.created_date)
        print("-----------------------------------------------")


def get_session():
    Session = sessionmaker(db)
    session = Session()
    return session


def setup_db():
    try:
        base.metadata.create_all(db)
        print("Database Created Successfully")
    except Exception as exp:
        print("Failed to create database, got exception: \n%s" % exp)
        print(traceback.format_exc())


if __name__ == '__main__':
    setup_db()
