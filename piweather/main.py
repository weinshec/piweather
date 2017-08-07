#!/usr/bin/env python
# encoding: utf-8

import argparse
import logging
import piweather

from piweather.sensors import Dummy
from piweather.measurements import Single


def run_dash():
    from piweather.dashboard.app import app
    app.run_server(debug=True, use_reloader=False)


def run_loop():
    from time import sleep
    logging.info("Press 'CTRL+C' to quit!")
    while True:
        try:
            sleep(1)
        except KeyboardInterrupt:
            break


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

    logging.info("Starting scheduler...")
    piweather.scheduler.start()

    # TODO: Make this dynamic later
    logging.info("Initializing sensors...")
    piweather.sensor_list["dummy0"] = Dummy()
    logging.info("Initializing sensors complete")
    logging.info("Initializing measurements...")
    piweather.measurement_list["dummy0_single"] = Single(
        piweather.sensor_list["dummy0"], frequency=5, table="dummy0_single")
    logging.info("Initializing measurements complete")

    if args.dash:
        run_dash()
    else:
        run_loop()

    logging.info("Stopping scheduler...")
    piweather.scheduler.shutdown(wait=True)
