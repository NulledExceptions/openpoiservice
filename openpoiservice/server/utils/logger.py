# -*- coding: utf-8 -*-

import os
import logging
from os.path import expanduser

def get_logger(name):
    log_format = '\n%(asctime)s  %(name)8s  %(levelname)5s  %(message)s'
    log_path = os.getenv('OPS_LOG', os.path.join([expanduser("~"), '/']))
    logging.basicConfig(level=logging.INFO,
                        format=log_format,
                        filename=os.path.join(log_path, 'ops.log'),
                        filemode='a')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(log_format))
    logging.getLogger(name).addHandler(console)
    return logging.getLogger(name)