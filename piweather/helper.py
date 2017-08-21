import importlib
import logging
import os
import sys


def load_external(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(path)

    logging.info("Loading {}".format(path))

    if sys.version_info[0] >= 3 and sys.version_info[1] >= 6:
        spec = importlib.util.spec_from_file_location("config", path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        return config
    else:
        config = importlib.machinery.SourceFileLoader("config", path)
        return config.load_module()
