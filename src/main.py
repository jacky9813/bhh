#!/usr/bin/python3
"""
    An example script for Better HTTP Handler
"""
import os
import sys
import http
import http.server
import bhh

@bhh.handle("GET","/test/{testvar}", optional_trail_slash=False)
def test(hdlr:bhh.HTTPRequestHandler, testvar):
    """
    An example function that returns what it received in the URI.
    """
    hdlr.send_response(http.HTTPStatus.OK)
    hdlr.send_header("Content-Type", "text/plain; charset=utf-8")
    hdlr.end_headers()
    hdlr.wfile.write((f"{testvar}").encode("utf-8"))

@bhh.handle("POST", "/echo")
def echo(hdlr: bhh.HTTPRequestHandler):
    """
    Echo the request body as plain text type.
    """
    if "Content-Length" in hdlr.headers:
        try:
            content_length = int(hdlr.headers["Content-Length"])
        except ValueError:
            hdlr.send_error(http.HTTPStatus.BAD_REQUEST)
            return
        hdlr.send_response(http.HTTPStatus.OK)
        hdlr.send_header("Content-Type", "text/plain; charset=utf-8")
        hdlr.end_headers()
        hdlr.wfile.write(hdlr.rfile.read(content_length))
    else:
        hdlr.send_error(http.HTTPStatus.BAD_REQUEST)
    

if __name__ == "__main__":
    HOST = os.environ["HOST"] if "HOST" in os.environ else "0.0.0.0"
    PORT = os.environ["PORT"] if "PORT" in os.environ else "8080"

    try:
        PORT = int(PORT)
    except ValueError:
        print(
            f"Warning: Invalid port specification: {PORT}, using default port 8080",
            file=sys.stderr
        )
        PORT = 8080

    server = http.server.HTTPServer(
        (HOST, PORT),
        bhh.HTTPRequestHandler
    )
    print(f"Listening on http://{HOST}:{PORT}")
    server.serve_forever()
