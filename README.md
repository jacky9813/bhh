# Better HTTP Handler (BHH)

This is a very basic HTTP Handler for Python built-in HTTP Server that opens up some easy way for web API development.

There're several benefits for using bhh:
* Easy to assign an URI to handle
* The usage is very similar to built-in HTTP server handler.
* Suitable for small projects.

## Create Handler

Very simple. Include the bhh and either use `bhh.register_handler` or `@bhh.handle`. Here're examples that does exact same thing:

```python
import bhh

def some_function(hdlr: bhh.HTTPRequestHandler):
    # Do something...
bhh.register_handler("POST", "/api/foo/bar", handler)
```

```python
import bhh

@bhh.handle("POST", "/api/foo/bar")
def some_function(hdlr: bhh.HTTPRequestHandler):
    # Do something...
```

## Variables in URI

It is suggested that any variable is enclosed by slashes, like `/api/foo/{var1}/bar`

Using a path like `/api/foo/{var1}bar` is discouraged and may cause problem.

```python
import bhh

@bhh.handle("GET", "/api/foo/{var1}/bar")
def some_foo(hdlr, var1):
    # Do something with var1...
```

## URI with trailing /

```python
@bhh.handle("GET", "/api/foo/bar")
def dont_care_trailing_slash(hdlr):
    # Do something

@bhh.handle("GET", "/api/bar/foo/")
def do_care_trailing_slash(hdlr):
    # Do somthing else
```

The following expression may cause unexpected behavior:
```python
@bhh.handle("GET", "/api/foo/bar")
def no_trailing_slash(hdlr):
    # Do something

@bhh.handle("GET", "/api/foo/bar/")
def with_trailing_slash(hdlr):
    # Do somthing else
```
Instead, if the function need to differentiate the behavior with/without the trailing slash:
```python
@bhh.handle("GET", "/api/foo/bar", optional_trail_slash=False)
def no_trailing_slash(hdlr):
    # Do something

@bhh.handle("GET", "/api/foo/bar/")
def with_trailing_slash(hdlr):
    # Do somthing else
```

## Get data from request body

```python
import http
import json
import bhh

@bhh.handle("POST", "/api/foo/bar")
def post_something(hdlr):
    try:
        data = json.load(hdlr.rfile)
    except:
        hdlr.send_response(http.HTTPStatus.BAD_REQUEST)
        hdlr.end_headers()
        return
    if data != None:
        # Do something...
```

## Static files

On working directory for the program, create a directory `static` and put anything static inside.

The handler will automatically grab the data inside if there's no `GET` handler for the URI.