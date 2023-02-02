#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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
import urllib.parse

from parso import parse
from zmq import PROTOCOL_ERROR_ZMTP_MALFORMED_COMMAND_UNSPECIFIED

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

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
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""
        
        parsedURL = urllib.parse.urlparse(url)
        host = parsedURL.hostname
        path = parsedURL.path
        port = parsedURL.port
        request = "GET "+  path +  " HTTP/1.1\r\nHost:" + host + "\n\n"
        
        if port != None:
            self.connect(host, port)
        else:
            self.connect(host, 80)
        
        self.sendall(request)
        
        body = self.recvall(self.socket)
        code = int(body.split()[1])

        self.close()


        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        request = "POST "
        parsedURL = urllib.parse.urlparse(url)
        host = parsedURL.hostname
        port = parsedURL.port
        path = parsedURL.path
        content_type = 'application/x-www-form-urlencoded'
        userAgent = "almostcURL/1.0"
       
        request += path + " HTTP/1.1\r\n"
        request += "HOST: " +  host + " \r\n"
        request += "User-Agent: " +  userAgent + " \r\n"
        request += "Content-Type: " +  content_type + " \r\n\r\n"
        # send a content length in here. 
        if args != None:
            i = 0
            for key in args:
                
                if i > 0:

                    request = request + "&" + key + "=" + args[key]
                else:
                    request = request + key + "=" + args[key]
                i +=1



        if port != None:
            self.connect(host, port)
        else:
            self.connect(host, 80)
        
        self.sendall(request)
        body = self.recvall(self.socket)
        code = int(body.split()[1])
        self.close()

        #You are not completing the body of your request. Something is wrong here and HTTP is waiting too long.
        #All post requests should have a content length header. 
        #
        return HTTPResponse(code, body)

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
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
