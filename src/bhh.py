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
import urllib.parse

INDEX_PAGE = [
    "index.html",
    "index.htm"
]
STATIC_PATH = os.path.realpath(os.path.join(os.getcwd(), "static"))

EXTERNAL_HANDLERS = {}
HANDLER_REGEXP = {}

def handle(method:str, path:str, optional_trail_slash=True):
    """
        Register the URI handler.
        Use this as a function decorator.

        Example:
        ```python
        @bhh.handle("POST", "/api/foo/{var1}/bar")
        def some_api(hdlr, var1):
            # Do something...
        ```
    """
    def deco(handler):
        register_handler(method, path, handler, optional_trail_slash)
    return deco

def register_handler(method:str, path:str , handler, optional_trail_slash=True):
    """
        Register the URI handler.

        Example:
        ```python
        def some_api(hdlr, var1):
            # Do something...
        bhh.register_handler("POST", "/api/foo/{var1}/bar", some_api)
        ```
    """
    if path not in EXTERNAL_HANDLERS:
        EXTERNAL_HANDLERS[path] = {
            "handlers": {},
            "regexp": re.compile(
                "^" +
                re.sub(r"\{([a-zA-Z0-9_]*)\}", "([^/]*)", path) +
                (r"/?$" if optional_trail_slash and path[-1]!="/" else r"$")
            ),
            "variables": re.findall(r"\{([a-zA-Z0-9_]*)\}", path)
        }
    EXTERNAL_HANDLERS[path]["handlers"][method] = handler


class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """
        The alternative for builtin HTTP handler.
    """
    server_version = "BHH/0.1"
    def address_string(self):
        """
        Return "client IP:port"
        """
        return f"{self.client_address[0]}:{self.client_address[1]}"
    def send_response(self, code, message=None):
        """Add the response header to the headers buffer and log the
        response code.

        Also send two standard headers with the server software
        version and the current date.

        """
        self.log_request(code)
        self.send_response_only(code, message)
        # self.send_header('Server', self.version_string())
        # self.send_header('Date', self.date_time_string())
        # Removes "Server: " and "Date: " header in default function
        # Developers can add it back as they wish.

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
            # Search if there's a match for the URI
            for k in EXTERNAL_HANDLERS:
                match = EXTERNAL_HANDLERS[k]["regexp"].search(self.path)
                if match is not None:
                    if self.command in EXTERNAL_HANDLERS[k]["handlers"]:
                        variables = {}
                        match_groups = match.groups()
                        for i in range(len(EXTERNAL_HANDLERS[k]["variables"])):
                            variables[EXTERNAL_HANDLERS[k]["variables"][i]] = \
                                urllib.parse.unquote(match_groups[i])
                        EXTERNAL_HANDLERS[k]["handlers"][self.command](self, **variables)
                        method = "external"
                    else:
                        self.send_error(
                            HTTPStatus.NOT_IMPLEMENTED,
                            f"Unsupported method ({repr(self.command)})")
                        return
                    break
            if method is None:
                self.send_error(
                    HTTPStatus.NOT_IMPLEMENTED,
                    f"Unsupported method ({repr(self.command)})")
                return
            if method != "external":
                method()
            self.wfile.flush() #actually send the response if not already done.
        except socket.timeout as err:
            #a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", err)
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
            fd = None
            if os.path.isfile(path):
                fd = open(path, mode="rb")
                t = path
            elif os.path.isdir(path):
                fd = None
                for i in INDEX_PAGE:
                    t = os.path.realpath(os.path.join(path,i))
                    if os.path.isfile(t):
                        fd = open(t, "rb")
                        break
            if fd:
                fs = os.fstat(fd.fileno())
                mime = mimetypes.guess_type(t)
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", mime[0])
                self.send_header("Content-Length", str(fs.st_size))
                self.end_headers()
                shutil.copyfileobj(fd, self.wfile)
            else:
                self.send_response(HTTPStatus.NOT_FOUND)
                self.send_header("Content-Length", "0")
                self.end_headers()
        