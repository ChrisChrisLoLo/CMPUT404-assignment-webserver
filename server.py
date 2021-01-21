#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/
import re, os

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        # print ("Got a request of: %s\n" % self.data)
        
        method, request_URI, _ = parse_request(self.data)
        # print(f'method: {method}, request_URI: {request_URI}')

        if method != 'GET':
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n\r\n405 Method Not Allowed",'utf-8'))
            return
        elif request_URI[-1] != '/' and '.' not in request_URI.split('/')[-1]:
            # print(f"failed: {request_URI.split('/')[-1]}")
            self.request.sendall(bytearray(f"HTTP/1.1 301 Moved Permanently\r\nLocation:{request_URI+'/'}\r\n\r\n301 Moved Permanently",'utf-8'))
            return

        self.get_request_URI(method, request_URI)

        # self.request.sendall(bytearray("HTTP/1.1 403 Forbidden\r\n\r\npoopy",'utf-8'))

    def get_request_URI(self, method, request_URI):
        URI_split = request_URI.split('/')[1:]
        if URI_split[-1] == '':
            URI_split[-1] = 'index.html'

        if not is_safe_URI_split(URI_split):
            self.request.sendall(bytearray(f"HTTP/1.1 404 Not Found\r\n\r\n404 Not Found",'utf-8'))
            return

        file_path = '/'.join(['.','www']+URI_split)
        if os.path.exists(file_path):
            res = 'HTTP/1.1 200 OK\r\n'
            content_type_header = ''
            if '.html' in URI_split[-1]:
                content_type_header = 'Content-Type: text/html\r\n'
            elif '.css' in URI_split[-1]:
                content_type_header = 'Content-Type: text/css\r\n'
            with open(file_path,'r') as file:
                data = '\r\n\r\n'+file.read()
            self.request.sendall(bytearray(res+content_type_header+data,'utf-8'))
            return
        else:
            # print(f'failed:{file_path}')
            self.request.sendall(bytearray(f"HTTP/1.1 404 Not Found\r\n\r\n404 Not Found",'utf-8'))
            return

        # print(URI_split)

# checks if the URI is attempting to access files outside of /www    
def is_safe_URI_split(URI_split):
    virtual_directory = []
    for directory in URI_split:
        if directory == '..':
            if len(virtual_directory) == 0:
                # out of bounds, unsafe
                return False
            else:
                virtual_directory.pop()
        else:
            virtual_directory.append(directory)
    return True

def parse_request(data):
    data_string = data.decode('ascii')
    # TODO: handle 0 index error
    request_line = data_string.split('\r\n')[0]
    method, request_URI, HTTP_version = request_line.split(' ')
    return method, request_URI, HTTP_version

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
