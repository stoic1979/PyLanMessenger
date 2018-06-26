import threading
import time
import random
from multiprocessing import Queue


BUF_SIZE = 10
q = Queue(BUF_SIZE)

class ProducerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ProducerThread,self).__init__()
        self.target = target
        self.name = name

    def run(self):
        while True:
            if not q.full():
                item = random.randint(1,10)
                q.put(item)
                print('Putting ' + str(item)  + ' : ' + str(q.qsize()) + ' items in queue')
                time.sleep(random.random())
        return

class ConsumerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ConsumerThread,self).__init__()
        self.target = target
        self.name = name
        return

    def run(self):
        while True:
            if not q.empty():
                item = q.get()
                print('Getting ' + str(item) 
                              + ' : ' + str(q.qsize()) + ' items in queue')
                time.sleep(random.random())
        return

if __name__ == '__main__':
    
    p = ProducerThread(name='producer')
    c = ConsumerThread(name='consumer')

    p.start()
    time.sleep(2)
    c.start()
    time.sleep(2)
