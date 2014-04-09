#!/usr/bin/env python
# -*- coding: utf-8 -*-


#You don't have to do this two lines if you are using in production trought pypi.
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

import unittest

from astrid.http.functional import WSGIClient, BenchmarkMixin
from astrid.web.wsgi import WSGIApplication

# My modules
from config import options

from main import *


application = WSGIApplication(options)


class AstridTestCase(unittest.TestCase):

    def runTest(self):
        self.setUp()

    def setUp(self):
        self.client = WSGIClient(application)

    def tearDown(self):
        del self.client
        self.client = None

    def test_template(self):
        """ Ensure welcome page is rendered."""
        assert 200 == self.client.get('/test_template')

    def test_no_template(self):
        """ Ensure welcome page is rendered."""
        assert 200 == self.client.get('/no_template')

    def test_html(self):
        """ Ensure welcome page is rendered."""
        assert 200 == self.client.get('/html')

    def test_form(self):
        """ Ensure welcome page is rendered."""
        assert 200 == self.client.get('/form')

    def test_form2(self):
        """ Ensure welcome page is rendered."""
        assert 200 == self.client.get('/form2')

    def test_session(self):
        """ Ensure welcome page is rendered."""
        assert 200 == self.client.get('/session')

    def test_not_found(self):
        """ Ensure not found status code. """
        assert 404 == self.client.get('/x')


class AstridTestBenchmark(AstridTestCase, BenchmarkMixin):
    """ Benchmark test case helper. """


if __name__ == "__main__":


    test_benchmark = AstridTestBenchmark()
    test_benchmark.setUp()
    benchmark = test_benchmark.benchmark((test_benchmark.test_template,
                                          test_benchmark.test_no_template,
                                          test_benchmark.test_html,
                                          test_benchmark.test_form,
                                          test_benchmark.test_form2,
                                          test_benchmark.test_session), 100)

    benchmark.report()






