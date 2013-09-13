#!/usr/bin/python
import cgi
import json

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep

from file_persister import FilePersister
from bid_solver import BidSolver

PORT_NUMBER = 8080

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/get_rankings':
            self.get_rankings()
            return
        if self.path == '/get_assignments':
            self.get_assignments()
            return

        if self.path == '/':
            self.path = '/bids.html'

        try:
            self.send_file(self.path)
        except IOError:
            self.send_error(404, 'File Not Found: {0}'.format(self.path))

    def send_file(self, path):
        if self.path.endswith('.html'):
            mimetype = 'text/html'
        elif self.path.endswith('.js'):
            mimetype = 'application/javascript'
        elif self.path.endswith('.css'):
            mimetype = 'text/css'
        elif self.path.endswith('.png'):
            mimetype = 'image/png'
        else:
            raise IOError()

        f = open(curdir + sep + path)
        self.send_response(200)
        self.send_header('Content-type', mimetype)
        self.end_headers()
        self.wfile.write(f.read())
        f.close()

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}

        if self.path == "/get_rankings":
            self.get_assignments()
        elif self.path == '/save':
            self.save(postvars)

    def get_rankings(self):
        self.send_response(200)
        self.end_headers()

        rankings_persister = FilePersister('rankings.dat')
        rankings = rankings_persister.get_all()
        #print rankings
        self.wfile.write(json.dumps(rankings))

    def get_assignments(self):
        rankings_persister = FilePersister('rankings.dat')
        rankings = rankings_persister.get_all()
        print rankings

        try: 
            assignments = BidSolver().get_assignments(rankings) 
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(assignments)) 
        except Exception as e:
            print e
            self.wfile.write(e)
            self.send_response(500)
            self.end_headers()

    def save(self, postvars):
        self.send_response(200)
        self.end_headers()
        
        # not sure why, but parsing postvars returns them in an array wrapper
        name = postvars['name'][0]
        pin = postvars['pin'][0]

        # verify pin
        pin_persister = FilePersister('pins.dat')
        stored_pin = pin_persister.get(name)
        if stored_pin != pin:
            self.wfile.write('Bad PIN!')
            return

        rankings_persister = FilePersister('rankings.dat')
        # the parser also renames ranking to ranking[]
        rankings_persister.save(name, postvars['ranking[]'])
        self.wfile.write('Saved!')
					
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
