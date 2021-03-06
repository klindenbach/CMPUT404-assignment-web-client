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
        try:
            ip = socket.gethostbyname(host)
        except socket.gaierror:
            #could not resolve hostanme
            print 'Hostname could not be resolved. Exiting'
            sys.exit()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            print 'Failed to create socket. Error code: ' + str(msg[0]) +\
                   ' , Error message : ' + msg[1]
            sys.exit();
            
        s.connect((ip, port))
           
        return s

    def get_code(self, data):
        code = 500
        if data.startswith("HTTP/1."):
            code = int(data[9:12])
        return code


    def get_headers(self,data):
        headers = ""
        headersEnd = data.find("\r\n\r\n")

        if headersEnd != -1:
            headers = data[:headersEnd]

        return headers

    def get_body(self, data):
        body = ""
        headersEnd = data.find("\r\n\r\n")

        if headersEnd != -1:
            body = data[headersEnd + 4:]

        return body

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
            try:
                port = int(host[firstColon + 1:])
            except ValueError:
                print "Port is not a valid integer"
                sys.exit()
            if (port < 0) or (port > 65535):
                print "Port is outside of allowable numbers"
                sys.exit()
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
        try:
            sock.sendall(self.getRequestStr("GET", path, headers))
        except socket.error:
            #sendall() failed
            print "sendall() failed."
            sys.exit()        
        sock.shutdown(socket.SHUT_WR)

        data = self.recvall(sock)
        code = self.get_code(data)
        body = self.get_body(data)

        sock.close()
        
        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        host, port, path = self.parseUrl(url)

        sock = self.connect(host, port)


        headers = {
            "User-Agent": "KBClient",
            "Host": host,
            "Accept": "*/*",
            "Content-Length": "0",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        variables = ""

        if args:
            variables = urllib.urlencode(args)
            headers["Content-Length"] = str(len(variables))
        
        try:
            sock.sendall(self.getRequestStr("POST", path, headers) + variables)
        except socket.error:
            #sendall() failed
            print "sendall() failed."
            sys.exit()
            
        sock.shutdown(socket.SHUT_WR)

        data = self.recvall(sock)
        code = self.get_code(data)
        body = self.get_body(data)

        sock.close()

        url, port, path = self.parseUrl(url)

        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        #Going to wrap this whole thing to handle timeouts
        try:
            if (command == "POST"): 
                return self.POST( url, args)
            else:
                return self.GET( url, args )
        except socket.timeout:
            print "Your request timed out."
        
    
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
