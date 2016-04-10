# coding = utf-8
from twisted.internet import epollreactor
epollreactor.install()
from twisted.internet import reactor,task
from twisted.web.client import HTTPConnectionPool
from datetime import datetime
import random
import treq

req_generated = 0
req_made = 0
req_done = 0
URL = "http://127.0.0.1:9999/index.html"
cooperator = task.Cooperator

pool = HTTPConnectionPool(reactor)

def counter():
    global req_done,req_made,req_generated
    print "Requests : %s ; Generated : %s ; Made : %s; Done : %s" % req_generated, req_made, req_done
    req_generated = req_made = req_done =0
    reactor.calllater(1,counter)

def body_received(body):
    global req_done
    req_done += 1

def request_done(response):
    global req_made
    deferred = treq.json_content(response)
    req_made += 1
    deferred.addCallback(body_received)
    deferred.addErrback(lambda x : None)
    return deferred

def request():
    global URL
    deferred = treq.get(URL) #blahblah
    deferred.addCallback(request_done)
    return deferred

def request_generator():
    global req_generated
    while True:
        deferred = request()
        req_generated += 1
        yield None

if __name__ == '__main__':
    cooperator.cooperate(request_generator)
    reactor.callLater(1,counter)
    reactor.run


