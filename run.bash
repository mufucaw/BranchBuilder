#!/bin/bash

gunicorn -w 5 -k gevent_wsgi Runner:wsgiapp
