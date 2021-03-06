import json
import time
import datetime
import logging

from src.estimator import estimator, sample_data

import xmltodict
import colors
from flask import Flask, request, make_response, g
from rfc3339 import rfc3339


def create_app():
    app = Flask(__name__)
    logger = app.logger

    f_handler = logging.FileHandler('estimator.logs')
    f_handler.setLevel(logging.INFO)

    f_format = logging.Formatter('%(message)s')

    f_handler.setFormatter(f_format)

    logger.addHandler(f_handler)

    @app.before_request
    def start_timer():
        g.start = time.time()

    @app.after_request
    def log_request(response):
        if request.path == '/favicon.ico':
            return response
        elif request.path.startswith('/static'):
            return response

        print('g.start')
        print(g.start)
        now = time.time()
        print('now')
        print(now)
        # duration = round(now - g.start, 2)
        duration = round((now - g.start) * 1000)
        print('duration')
        print(duration)
        dt = datetime.datetime.fromtimestamp(now)
        timestamp = rfc3339(dt, utc=True)

        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        host = request.host.split(':', 1)[0]
        args = dict(request.args)

        log_params = [
            ('method', request.method, 'blue'),
            ('path', request.path, 'blue'),
            ('status', response.status_code, 'yellow'),
            ('duration', f'{duration}ms', 'green'),
            ('time', timestamp, 'magenta'),
            ('ip', ip, 'red'),
            ('host', host, 'red'),
            ('params', args, 'blue')
        ]

        request_id = request.headers.get('X-Request-ID')
        if request_id:
            log_params.append(('request_id', request_id, 'yellow'))

        parts = []
        for name, value, color in log_params:
            part = colors.color("{}={}".format(name, value), fg=color)
            parts.append(part)
        line = " ".join(parts)
        app.logger.info(
            f'{request.method} {request.path} '
            f'{response.status_code} {duration}ms')
        return response

    @app.route('/api/v1/on-covid-19')
    def covid_default():

        return estimator(sample_data)

    @app.route('/api/v1/on-covid-19/json')
    def covid_json():

        return estimator(sample_data)

    @app.route('/api/v1/on-covid-19/xml')
    def covid_xml():
        data = estimator(sample_data)
        xml_data = xmltodict.unparse({"data": data}, pretty=True)
        response = make_response(xml_data)
        response.headers['Content-Type'] = 'application/xml'
        return response

    @app.route('/api/v1/on-covid-19/logs')
    def logs():
        with open('estimator.logs', 'r') as f:
            log_file = f.read()
            response = make_response(log_file)
            response.headers['Content-Type'] = 'text/plain'
        return response

    return app
