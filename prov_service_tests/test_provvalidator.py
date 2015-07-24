"""Test class for ProvValidator service``.
"""
# Copyright (c) 2015 University of Southampton
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions: 
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software. 
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.  

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import itertools
import json
import os
import requests
import unittest
from nose.tools import istest
from nose_parameterized import parameterized

from prov_service_tests import http
from prov_service_tests import standards
from prov_service_tests.test_service import ServiceTestCase

@istest
class ProvValidatorTestCase(ServiceTestCase):
  """Test class for ProvValidator service. These tests check that
  ProvValidator is available and responds to requests directed 
  against its  
  `REST API <https://provenance.ecs.soton.ac.uk/validator/view/api.html>`_.
  """

  URL_ENV = "PROVVALIDATOR_URL"
  """str or unicode: environment variable holding ProvValidator URL
  """

  CONTENT_TYPES = {
    standards.PROVN: "text/provenance-notation",
    standards.TTL: "text/turtle",
    standards.TRIG: "application/trig",
    standards.PROVX: "application/provenance+xml",
    standards.JSON: "application/json"
   }
  """dict: mapping from formats in ``prov_service_tests.standards`` to
    content types """

  def setUp(self):
    super(ProvValidatorTestCase, self).setUp()
    self.url = os.environ[ProvValidatorTestCase.URL_ENV]

  def tearDown(self):
    super(ProvValidatorTestCase, self).tearDown()

  @parameterized.expand(list(itertools.product(standards.FORMATS, 
                                               standards.FORMATS)))
  def test_translate(self, format1, format2):
    """Test POST /provapi/documents/ on translations between formats.
    """
    headers = {http.CONTENT_TYPE: ProvValidatorTestCase.CONTENT_TYPES[format1],
               http.ACCEPT: ProvValidatorTestCase.CONTENT_TYPES[format2]}
    response = requests.post(self.url, 
                             headers=headers, 
                             data=self.get_primer(format1))
    self.assertEqual(requests.codes.ok, response.status_code)

  @parameterized.expand(standards.FORMATS)
  def test_validate(self, format):
    """Test POST /provapi/documents/ with validate:Validate.
    """
    response = requests.post( \
      self.url, 
      headers={http.ACCEPT: "text/html"},
      files={"statements": self.get_primer(format)},
      data={"validate": "Validate", "type": format})
    self.assertEqual(requests.codes.ok, response.status_code)

  def test_get_document(self):
    """Test GET /provapi/documents/{docId} and GET /provapi/documents/{docId}/original.
    """
    # POST /provapi/documents/
    headers={http.CONTENT_TYPE: 
             ProvValidatorTestCase.CONTENT_TYPES[standards.JSON]}
    response = requests.post( \
      self.url,
      headers=headers,
      allow_redirects=False,
      data=self.get_primer(standards.JSON))
    self.assertEqual(requests.codes.see_other, response.status_code)
    # GET /provapi/documents/{docId}
    graph_url = response.headers["location"]
    response = requests.get(graph_url, allow_redirects=False)
    self.assertEqual(requests.codes.see_other, response.status_code) 
    # GET /provapi/documents/{docId}/original
    response = requests.get(graph_url + "/original", allow_redirects=False)
    self.assertEqual(requests.codes.ok, response.status_code)

  @parameterized.expand(standards.FORMATS)
  def test_get_document_type(self, format):
    """Test GET /provapi/documents/{docId}.{type}.
    """
    # POST /provapi/documents/
    headers={http.CONTENT_TYPE: 
             ProvValidatorTestCase.CONTENT_TYPES[standards.JSON]}
    response = requests.post( \
      self.url,
      headers=headers,
      allow_redirects=False,
      data=self.get_primer(standards.JSON))
    self.assertEqual(requests.codes.see_other, response.status_code)
    graph_url = response.headers["location"]
    # GET /provapi/documents/{docId}.{type}
    response = requests.get(graph_url + "." + format)
    self.assertEqual(requests.codes.ok, response.status_code)

  def test_get_validation_report(self):
    """Test POST /provapi/documents/validation/report and report.xml
    """
    # POST /provapi/documents/
    response = requests.post( \
      self.url, 
      files={"statements": self.get_primer(standards.JSON)},
      data={"validate": "Validate", 
            "type": standards.JSON},
      allow_redirects=False)
    self.assertEqual(requests.codes.see_other, response.status_code)
    # GET /provapi/documents/{docId}/validation/report
    report_url = response.headers["location"]
    response = requests.get(report_url)
    self.assertEqual(requests.codes.ok, response.status_code)
    # GET /provapi/documents/{docId}/validation/report.xml
    response = requests.get(report_url + ".xml")
    self.assertEqual(requests.codes.ok, response.status_code)

    # How to get graphNNNN more nicely?
    # Does it work for translated documents?
 
    print(report_url)
    validation_url = report_url.replace("/report", "")
    print(validation_url)
    graph_url = validation_url.replace("/validation", "")
    print(graph_url)

    # GET /provapi/documents/{docId}/metrics Graph metrics
    print(graph_url + "/metrics")
    response = requests.get(graph_url + "/metrics")
#    print(response.headers)
#    print(response.text)
    self.assertEqual(requests.codes.ok, response.status_code)

    # GET /provapi/documents/{docId}/validation/normalForm
    response = requests.get(validation_url + "/normalForm")
#    print(response.headers)
#    print(response.text)
    self.assertEqual(requests.codes.ok, response.status_code)
    # GET /provapi/documents/{docId}/validation/normalForm.{type}
    for f in standards.FORMATS:
      response = requests.get(validation_url + "/normalForm" + "." + f)
#      print(response.headers)
#      print(response.text)
      self.assertEqual(requests.codes.ok, response.status_code)

    # GET /provapi/documents/{docId}/validation/matrix - no information resource
    # Ignore
    # GET /provapi/documents/{docId}/validation/matrix.txt
    response = requests.get(validation_url + "/matrix.txt")
#    print(response.headers)
#    print(response.text)
    self.assertEqual(requests.codes.ok, response.status_code)
    # GET /provapi/documents/{docId}/validation/matrix.png
    response = requests.get(validation_url + "/matrix.png")
#    print(response.headers)
#    print(response.text)
    self.assertEqual(requests.codes.ok, response.status_code)
    response = requests.get(validation_url + "/matrix/diagonal")
#    print(response.headers)
#    print(response.text)
    self.assertEqual(requests.codes.ok, response.status_code)

  def test_get_random_nodes_degree(self):
    """Test GET /provapi/documents/random/{nodes}/{degree}
    """
    response = requests.get(self.url + "random/1/1")
    self.assertEqual(requests.codes.ok, response.status_code)

  def test_get_random_nodes_degree_seed(self):
    """Test GET /provapi/documents/random/{nodes}/{degree}/{seed}
    """
    response = requests.get(self.url + "random/1/1/1")
    self.assertEqual(requests.codes.ok, response.status_code)
