#!/usr/bin/env python
# encoding: utf-8

import argparse
import logging
import piweather
import sys
import time

from piweather.dashboard import create_app
from piweather.helper import load_external


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
        piweather.config = load_external(args.config)
        sensors = load_external(piweather.config.SENSORS)
        piweather.config.SENSORS = sensors.SENSORS
        piweather.config.MEASUREMENTS = sensors.MEASUREMENTS
    except FileNotFoundError:
        logging.error("Config file not found at {}".format(args.config))
        sys.exit(1)

    piweather.scheduler.start()
    if args.dash:
        piweather.app = create_app()
        piweather.app.run_server(
            host=piweather.config.HOSTS,
            port=piweather.config.PORT,
            use_reloader=False)
    else:
        logging.info("Press 'CTRL+C' to quit!")
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
    piweather.scheduler.shutdown(wait=True)
