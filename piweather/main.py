#!/usr/bin/env python
# encoding: utf-8

import argparse
import importlib.util
import logging
import piweather


def run_dash():
    from piweather.dashboard.app import app
    app.run_server(debug=True, use_reloader=False, host="0.0.0.0")


def run_loop():
    from time import sleep
    logging.info("Press 'CTRL+C' to quit!")
    while True:
        try:
            sleep(1)
        except KeyboardInterrupt:
            break


def initialize():
    logging.info("Starting scheduler...")
    piweather.scheduler.start()

    # TODO: config.py path should specifyable
    logging.info("Initializing sensors and measurments")
    spec = importlib.util.spec_from_file_location(
        "config", "/home/weinshec/workspace/piweather/config.py")
    piweather.config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(piweather.config)
    logging.info("Initialation complete")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="piweather Automatic Weather Station")
    parser.add_argument("--dash", action="store_true",
                        help="run dashboard server")
    parser.add_argument("--debug", action="store_true",
                        help="enable debug output")
    args = parser.parse_args()

    logLevel = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format="{asctime}|{levelname:7s}|> {message}",
                        style="{", datefmt="%d/%m/%Y %H:%M:%S", level=logLevel)

    initialize()

    if args.dash:
        run_dash()
    else:
        run_loop()

    logging.info("Stopping scheduler...")
    piweather.scheduler.shutdown(wait=True)
