#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

#__all__ = ['warn', 'error', 'info', 'debug']

logging.basicConfig(level=logging.INFO)


"""
log = logging.getLogger('astrid_app')

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

log.addHandler(ch)


def warn(msg):
    log.warning(msg)


def error(msg):
    log.error(msg)


def info(msg):
    log.info(msg)


def debug(msg):
    log.debug(msg)
"""