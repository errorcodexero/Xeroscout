# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 11:52:00 2019

@author: scout
"""

import logging
import datetime

logging.basicConfig(
    filename = 'test.log',
    level=logging.DEBUG
)
logging.debug("Test entry" + str(datetime.datetime.now()))
