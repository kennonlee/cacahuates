#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import cgi

from gdoc_fetcher import GdocFetcher

PORT_NUMBER = 8080

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
    
    #Handler for the GET requests
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        try:
            assignments = GdocFetcher("kennonator@gmail.com", "gobbledygook").get_assignments()
            self.wfile.write('<ul>')
            for ass in assignments:
                self.wfile.write('<li>{0} assigned to {1} (#{2} pick)</li>'.format(*ass))
            self.wfile.write('</ul>')
        except Exception as e:
            self.wfile.write(e)

        return

    #Handler for the POST requests
    def do_POST(self):
        if self.path=="/send":
            form = cgi.FieldStorage(
                fp=self.rfile, 
                headers=self.headers,
                environ={'REQUEST_METHOD':'POST',
                         'CONTENT_TYPE':self.headers['Content-Type'],
                         })

            print "Your name is: %s" % form["your_name"].value
            self.send_response(200)
            self.end_headers()
            self.wfile.write("Thanks %s !" % form["your_name"].value)
            return			
					
try:
    #Create a web server and define the handler to manage the
    #incoming request
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print 'Started httpserver on port ' , PORT_NUMBER
	
    #Wait forever for incoming htto requests
    server.serve_forever()

except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    server.socket.close()
