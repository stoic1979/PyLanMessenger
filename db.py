#
# wrapper for database transactions
#

from models import Message, get_session


class Db:

    def __init__(self):
        self.session = get_session()

    def add_msg(self, sender_host, sender_ip, receiver_host, receiver_ip, body):
        m = Message(sender_host, sender_ip, receiver_host, receiver_ip, body)
        self.session.add(m)
        self.session.commit()

    def get_all_msgs(self):
        return self.session.query(Message).all()


def quick_tests():
    db = Db()
    db.add_msg("Navi", "192.168.1.18", "Tom", "192.168.1.20", "Hello from navi")
    for msg in db.get_all_msgs():
        print (msg.to_dict())
        msg.log()

if __name__ == '__main__':
    quick_tests()
