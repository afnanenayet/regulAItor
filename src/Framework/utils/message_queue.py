# File: /Framework/utils/message_queue.py

import threading
import queue

class MessageQueue:
    def __init__(self):
        self.queue = queue.Queue()
        self.subscribers = []

    def publish(self, message):
        self.queue.put(message)
        for subscriber in self.subscribers:
            threading.Thread(target=subscriber.process_message, args=(message,)).start()

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)
