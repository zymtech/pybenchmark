# pybenchmark
A Replacement of ApacheBenchmark Written in Python

#Usage
Just run the main.py with options and url.

Options:

      -h, --help            Show this help message and exit
      --version             Displays version and exits.
      -C, --cookies COOKIES Add cookies (eg: 'id=1234'.(repeatable)) with requests.
      -P, --proxyauth USERNAME:PASSWORD
                            Add basic proxy authentication, use a colon to seperate
                            username and password.
      -X, --proxy PROXY     Configure proxy, server and port to use.
      -p, --profile         Run program under python profile, default to FALSE.
      -m {GET,POST,DELETE,PUT,HEAD,OPTIONS}, --method {GET,POST,DELETE,PUT,HEAD,OPTIONS}
                            HTTP Method
      --content-type CONTENT_TYPE
                            Content-Type
      -D DATA, --data DATA  Data. Prefixed by "py:" to point a python callable.
      -c CONCURRENCY, --concurrency CONCURRENCY
                            Concurrency
      -a AUTH, --auth AUTH  Basic authentication user:password
      --header HEADER       Custom header. name:value
      --pre-hook PRE_HOOK   Python module path (eg: mymodule.pre_hook) to a
                            callable which will be executed before doing a request
                            for example: pre_hook(method, url, options). It must
                            return a tupple of parameters given in function
                            definition
      --post-hook POST_HOOK
                            Python module path (eg: mymodule.post_hook) to a
                            callable which will be executed after a request is
                            done for example: eg. post_hook(response). It must
                            return a given response parameter or raise an
                            `boom._boom.RequestException` for failed request.
      --json-output         Prints the results in JSON instead of the default
                            format
      -n REQUESTS, --requests REQUESTS
                            Number of requests
      -d DURATION, --duration DURATION
                            Duration in seconds


