#!/usr/bin/env python
# encoding: utf-8

import argparse
import importlib.util
import logging
import os
import piweather
import sys
import time


def run_dash():
    from piweather.dashboard.app import app
    app.run_server(host="0.0.0.0", use_reloader=False)


def run_loop():
    logging.info("Press 'CTRL+C' to quit!")
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break


def load_config(path):
    if not os.path.isfile(path):
        raise FileNotFoundError

    logging.info("Loading config from {}".format(path))
    spec = importlib.util.spec_from_file_location("config", path)
    piweather.config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(piweather.config)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="piweather Automatic Weather Station")
    parser.add_argument("-c --config", metavar="PATH", dest="config",
                        default="test/static/config.py",
                        help="specify the config file to use")
    parser.add_argument("--dash", action="store_true",
                        help="run dashboard server")
    parser.add_argument("--debug", action="store_true",
                        help="enable debug output")
    args = parser.parse_args()

    logLevel = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format="{asctime}|{levelname:7s}|> {message}",
                        style="{", datefmt="%d/%m/%Y %H:%M:%S", level=logLevel)
    if not args.debug:
        logging.getLogger('apscheduler.executors.default').propagate = False

    try:
        load_config(args.config)
    except FileNotFoundError:
        logging.error("Config file not found at {}".format(args.config))
        sys.exit(1)

    piweather.scheduler.start()
    if args.dash:
        run_dash()
    else:
        run_loop()
    piweather.scheduler.shutdown(wait=True)
