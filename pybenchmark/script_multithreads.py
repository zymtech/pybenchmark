# coding = utf-8
import threading
import time
import requests

HOST = "127.0.0.1:9999"
PORT = 9999
URL = "/index.html"
THREAD_COUNT = 40
TEST_COUNT = 1000
SUC = 0


class RequestThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.test_count = 0

    def run(self):
        for _ in range(TEST_COUNT):
            self.test_performance()

    def test_performance(self):
        global SUC
        try:
            response = requests.get('http://'+HOST+URL)
            if response.status_code == 200:
                SUC += 1
            self.test_count += 1
        except BaseException as e:
            print e


if __name__ == '__main__':
    start_time = time.time()
    threads = []
    for i in range(THREAD_COUNT):
        thread = RequestThread()
        threads.append(thread)
        thread.start()
    word = ''
    while True:
        word = raw_input("enter 's' to check current status , or 'x' to stop : ")
        if word == 's':
            time_span = time.time() - start_time
            all_count = 0
            for t in threads:
                all_count += t.test_count
            print "%s total count" % all_count
            print "%s successful requests " % SUC
            print "%s failed requests " % (all_count - SUC)
            print "%s Request/Second " % str(all_count / time_span)
        elif word == 'x':
            for t in threads:
                t.join(0)
            break
