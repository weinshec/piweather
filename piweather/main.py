#!/usr/bin/env python
# encoding: utf-8

import argparse
import logging

from piweather import scheduler


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="piweather Automatic Weather Station")
    parser.add_argument('--debug', action='store_true',
                        help='enable debug output')
    args = parser.parse_args()

    logLevel = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format="{asctime}|{levelname:7s}|> {message}",
                        style="{", datefmt="%d/%m/%Y %H:%M:%S", level=logLevel)

    logging.info("Starting scheduler...")
    scheduler.start()
