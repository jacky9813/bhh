"""
    Better HTTP Handler (BHH)

    Based on the builtin http module, but easier for implementing simple API calls.
"""
import http.server
from http import HTTPStatus
import mimetypes
import os
import shutil
import socket
import re
import sys

INDEX_PAGE = [
    "index.html",
    "index.htm"
]
STATIC_PATH = os.path.realpath(os.path.join(os.getcwd(), "static"))

EXTERNAL_HANDLERS = {}
HANDLER_REGEXP = {}

def handle(method:str, path:str):
    def a(handler):
        register_handler(method, path, handler)
    return a

def register_handler(method:str, path:str , handler):
    if path not in EXTERNAL_HANDLERS:
        EXTERNAL_HANDLERS[path] = {
            "handlers": {},
            "regexp": re.compile("^" + re.sub(r"\{([a-zA-Z0-9_]*)\}", "([^/]*)", path) + r"/?$"),
            "variables": re.findall(r"\{([a-zA-Z0-9_]*)\}", path)
        }
    EXTERNAL_HANDLERS[path]["handlers"][method] = handler


class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """
        The alternative for builtin HTTP handler.
    """
    server_version = "BHH/0.1"
    def log_message(self, format, *args):
        sys.stderr.write(f"{self.log_date_time_string()} - {self.address_string()} - {format%args}\n")
    def address_string(self):
        return f"{self.client_address[0]}:{self.client_address[1]}"

    def send_response(self, code, message=None):
        """Add the response header to the headers buffer and log the
        response code.

        Also send two standard headers with the server software
        version and the current date.

        """
        self.log_request(code)
        self.send_response_only(code, message)
        self.send_header('Date', self.date_time_string())

    def handle_one_request(self):
        """Handle a single HTTP request.

        You normally don't need to override this method; see the class
        __doc__ string for information on how to handle specific HTTP
        commands such as GET and POST.

        """
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                return
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                # An error code has been sent, just exit
                return
            mname = 'do_' + self.command
            method = None
            if hasattr(self, mname):
                method = getattr(self, mname)
            for k in EXTERNAL_HANDLERS:
                m = EXTERNAL_HANDLERS[k]["regexp"].search(self.path)
                if m is not None:
                    # Match found
                    if self.command in EXTERNAL_HANDLERS[k]["handlers"]:
                        variables = {}
                        match_groups = m.groups()
                        for i in range(len(EXTERNAL_HANDLERS[k]["variables"])):
                            variables[EXTERNAL_HANDLERS[k]["variables"][i]] = match_groups[i]
                        EXTERNAL_HANDLERS[k]["handlers"][self.command](self, **variables)
                        method = "external"
                    break
            if method is None:
                self.send_error(
                    HTTPStatus.NOT_IMPLEMENTED,
                    "Unsupported method (%r)" % self.command)
                return
            if method != "external":
                method()
            self.wfile.flush() #actually send the response if not already done.
        except socket.timeout as e:
            #a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = True
            return

    def do_GET(self):
        path = os.path.realpath(STATIC_PATH + self.path)
        if path[:len(STATIC_PATH)] != STATIC_PATH:
            # Real path is not inside static.
            self.send_response(HTTPStatus.FORBIDDEN)
            self.send_header("Content-Length", "0")
            self.end_headers()
        else:
            f = None
            if os.path.isfile(path):
                f = open(path, mode="rb")
                t = path
            elif os.path.isdir(path):
                f = None
                for i in INDEX_PAGE:
                    t = os.path.realpath(os.path.join(path,i))
                    if os.path.isfile(t):
                        f = open(t, "rb")
                        break
            if f:
                fs = os.fstat(f.fileno())
                mime = mimetypes.guess_type(t)
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", mime[0])
                self.send_header("Content-Length", str(fs.st_size))
                self.end_headers()
                shutil.copyfileobj(f, self.wfile)
            else:
                self.send_response(HTTPStatus.NOT_FOUND)
                self.send_header("Content-Length", "0")
                self.end_headers()
        