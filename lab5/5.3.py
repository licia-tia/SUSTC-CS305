from socket import *
from dnslib import DNSRecord
import time


remoteServer = '8.8.8.8'
localPort = 53


def query(query_data, remote_server, local_port):
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.sendto(query_data, (remote_server, local_port))
    response, server_address = client_socket.recvfrom(2048)
    return response


serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', localPort))
print("Server started")

cache = {}
die_time = {}

while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    print('Request Inbound')
    request = DNSRecord.parse(message)
    question = request.questions
    rid = request.header.id

    if cache.get(repr(question)):
        reply = cache.get(repr(question))
        print('hit')
        if time.time()>die_time[repr(question)]:
            print('outdated')
            reply = query(message, remoteServer, localPort)
            readable_reply = DNSRecord.parse(reply)
            min_ttl = 600
            for x in readable_reply.rr:
                if x.ttl < min_ttl:
                    min_ttl = x.ttl

            for x in readable_reply.rr:
                x.ttl = min_ttl
            cache[repr(question)] = DNSRecord.pack(readable_reply)
            die_time[repr(question)] = time.time() + readable_reply.a.ttl
            print('required')
        else:
            readable_reply = DNSRecord.parse(reply)
            readable_reply.header.id = rid
            for x in readable_reply.rr:
                x.ttl = int(die_time[repr(question)]-time.time())
            reply = DNSRecord.pack(readable_reply)
    else:
        reply = query(message, remoteServer, localPort)

        readable_reply = DNSRecord.parse(reply)
        min_ttl = 600
        for x in readable_reply.rr:
            if x.ttl < min_ttl:
                min_ttl = x.ttl

        for x in readable_reply.rr:
            x.ttl = min_ttl
        cache[repr(question)] = DNSRecord.pack(readable_reply)
        die_time[repr(question)] = time.time()+readable_reply.a.ttl
        print('required')

    serverSocket.sendto(DNSRecord.pack(readable_reply), clientAddress)
    print('answers sent')
    print('-----------------------------------------------------')

