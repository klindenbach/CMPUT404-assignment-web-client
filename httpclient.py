#!/usr/bin/env python
# coding: utf-8
# Copyright 2015 Abram Hindle, Konrad Lindenbach, Ben Dubois
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def __str__(self):
       return self.body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        ip = socket.gethostbyname(host)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))

        return s

    def get_code(self, data):
        return None

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def parseUrl(self, url):
        if url.startswith("http://"):
            url = url[7:]

        firstSlash = url.find('/')
        
        if firstSlash == -1:
            path = '/'
            host = url
        else:
            path = url[firstSlash:]
            host = url[:firstSlash]

        port = 80

        firstColon = host.find(':')

        if firstColon != -1:
            port = int(host[firstColon + 1:])
            host = host[:firstColon]

        return host, port, path

    def getRequestStr(self, command, path, headers):

        request = command + " " + path + " " + "HTTP/1.1\r\n"

        for header in headers.keys():
            request += header + ": " + headers[header] + "\r\n"

        request += "\r\n"

        return request

    def GET(self, url, args=None):
        code = 500
        body = ""

        host, port, path = self.parseUrl(url)

        sock = self.connect(host, port)

        headers = {
            "User-Agent": "KBClient",
            "Host": host,
            "Accept": "*/*"
        }

        sock.sendall(self.getRequestStr("GET", path, headers))
        sock.shutdown(socket.SHUT_WR)

        body = self.recvall(sock)
        if body.startswith("HTTP/1."):
            code = int(body[9:12])

        headersEnd = body.find("\r\n\r\n")

        if headersEnd != -1:
            body = body[headersEnd + 4:]

        sock.close()
        
        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        url, port, path = self.parseUrl(url)

        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( command, sys.argv[1] )    
