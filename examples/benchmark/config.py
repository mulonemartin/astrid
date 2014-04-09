#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


__all__ = ['options']


options = {
        'SERVER': 'wsgiref',
        'IP': '0.0.0.0',
        'PORT': 8000,
        'TEMPLATES_FOLDER': 'templates/',
        'STATIC_FOLDER': os.path.abspath('../static')
    }