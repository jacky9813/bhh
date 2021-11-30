
import os
import http
import http.server
import bhh

HOST = os.environ["HOST"] if "HOST" in os.environ else "0.0.0.0"
PORT = os.environ["PORT"] if "PORT" in os.environ else "8080"

server = http.server.HTTPServer(
    (HOST, int(PORT)),
    bhh.HTTPRequestHandler
)

@bhh.handle("GET","/test/{testvar}", optional_trail_slash=False)
def test(hdlr:bhh.HTTPRequestHandler, testvar):
    hdlr.send_response(http.HTTPStatus.OK)
    hdlr.send_header("Content-Type", "text/html; charset=utf-8")
    hdlr.end_headers()
    hdlr.wfile.write((f"<!DOCTYPE html><html><body>{testvar}</body></html>").encode("utf-8"))

print(f"Listening on http://{HOST}:{PORT}")
server.serve_forever()
