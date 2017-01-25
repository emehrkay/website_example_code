# How to Get Started with Gremlin Server and Gizmo (Python)

Support files for the article []()

## Requirements

* Python 3.5+
* Java 8
* TinkerPop Gremlin Server
* Tornadoweb
* Websokets
* Gizmo
* Gremlinpy
* Read []()

## Setup

I'd recommend running this in a virtual environment.

1. clone the project
1. `cd /to/project/`
1. `pyvenv env`
1. `pip install -r requirements`
1. `pip install -e /path/to/where/you/cloned/gizmo/`
1. Run to create a default user `python default_data.py` Save the generated `id` and edit `USER_ID` in server.py
1. `python server.py` -- the server should be running on port 9999
