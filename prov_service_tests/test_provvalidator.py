"""Test class for ProvValidator service.
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
  against the 
  `ProvValidator REST API <https://provenance.ecs.soton.ac.uk/validator/view/api.html>`_.

  The class expects one environment variable to be set:

  - ``PROVVALIDATOR_URL`` - ProvValidator base URL e.g.
    ``https://provenance.ecs.soton.ac.uk/validator/provapi/documents/``
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
  """dict: mapping from :mod:`prov_service_tests.standards` formats to
  content types understood by ProvStore
  """

  def setUp(self):
    super(ProvValidatorTestCase, self).setUp()
    self.url = os.environ[ProvValidatorTestCase.URL_ENV]

  def tearDown(self):
    super(ProvValidatorTestCase, self).tearDown()

  def post_translate(self, document, format=standards.JSON):
    """Submit POST /provapi/documents to translate a document. The
    request is requested not to allow redirects and a test is done to
    check that the response code is 303 SEE OTHER.
  
    :param document: document in given format
    :type document: str or unicode
    :param format: a :mod:`prov_service_tests.standards` format
    :type format: str or unicode
    :return: URL of stored document
    :rtype: :class:`requests.Response`
    """
    headers={http.CONTENT_TYPE: 
             ProvValidatorTestCase.CONTENT_TYPES[format]}
    response = requests.post( \
      self.url,
      headers=headers,
      allow_redirects=False,
      data=document)
    self.assertEqual(requests.codes.see_other, response.status_code)
    return response

  @parameterized.expand(list(itertools.product(standards.FORMATS, 
                                               standards.FORMATS)))
  def test_post_translate(self, format1, format2):
    """Test POST /provapi/documents/ for translation.
    """
    headers = {http.CONTENT_TYPE: ProvValidatorTestCase.CONTENT_TYPES[format1],
               http.ACCEPT: ProvValidatorTestCase.CONTENT_TYPES[format2]}
    response = requests.post(self.url, 
                             headers=headers, 
                             data=self.get_primer(format1))
    self.assertEqual(requests.codes.ok, response.status_code)

  def test_translate_get_document(self):
    """Test GET /provapi/documents/{docId}.
    """
    response = self.post_translate(self.get_primer(standards.JSON),
                                   standards.JSON)

    graph_url = response.headers["location"]
    response = requests.get(graph_url)
    self.assertEqual(requests.codes.ok, response.status_code)

  def test_translate_get_document_original(self):
    """Test GET /provapi/documents/{docId}/original.
    """
    response = self.post_translate(self.get_primer(standards.JSON),
                                   standards.JSON)

    graph_url = response.headers["location"]
    response = requests.get(graph_url + "/original")
    self.assertEqual(requests.codes.ok, response.status_code)

  @parameterized.expand(standards.FORMATS)
  def test_translate_get_document_type(self, format):
    """Test GET /provapi/documents/{docId}.{type}.
    """
    response = self.post_translate(self.get_primer(standards.JSON),
                                   standards.JSON)

    graph_url = response.headers["location"]
    response = requests.get(graph_url + "." + format)
    self.assertEqual(requests.codes.ok, response.status_code)

  @parameterized.expand(standards.FORMATS)
  def test_post_validate(self, format):
    """Test POST /provapi/documents for validation.
    """
    response = requests.post( \
      self.url, 
      files={"statements": self.get_primer(format)},
      data={"validate": "Validate", 
            "type": format},
      allow_redirects=True)
    self.assertEqual(requests.codes.ok, response.status_code)

  def validate(self):
    """Submit POST /provapi/documents then GET
      /provapi/documents/{docId}/validation/report to validate
      document.

    - Submit POST /provapi/documents request with a JSON document.
    - Get the graph URL from the response header ``location`` field. 
    - Submit GET /provapi/documents/{docId}/validation/report,
      to validate the document. 
    - Test that the response to GET is 200 OK. 

    Accessing the validation report is a pre-requisite of
    validation-related requests including /validation, /metrics,
    /normalForm and /matrix.

    :return: graph URL
    :rtype: str or unicode
    """
    response = self.post_translate(self.get_primer(standards.JSON),
                                   standards.JSON)
    graph_url = response.headers["location"]
    response = requests.get(graph_url + "/validation/report")
    self.assertEqual(requests.codes.ok, response.status_code)
    return graph_url

  def test_get_metrics(self):
    """Test GET /provapi/documents/{docId}/metrics.
    """
    graph_url = self.validate()

    response = requests.get(graph_url + "/metrics")
    self.assertEqual(requests.codes.ok, response.status_code)

  @parameterized.expand(["txt", "png"])
  def test_get_validation_matrix_format(self, format):
    """Test GET /provapi/documents/{docId}/validation/matrix.txt and png.
    """
    graph_url = self.validate()

    response = requests.get(graph_url + "/validation/matrix." + format)
    self.assertEqual(requests.codes.ok, response.status_code)

  def test_get_validation_matrix_diagonal(self):
    """Test GET /provapi/documents/{docId}/validation/matrix/diagonal.
    """
    graph_url = self.validate()

    response = requests.get(graph_url + "/validation/matrix/diagonal")
    self.assertEqual(requests.codes.ok, response.status_code)

  def test_get_validation_normal_form(self):
    """Test GET /provapi/documents/{docId}/validation/normalForm.
    """
    graph_url = self.validate()

    response = requests.get(graph_url + "/validation/normalForm")
    self.assertEqual(requests.codes.ok, response.status_code)

  @parameterized.expand(standards.FORMATS)
  def test_get_validation_normal_form_format(self, format):
    """Test GET /provapi/documents/{docId}/validation/normalForm.{type}.
    """
    graph_url = self.validate()

    response = requests.get(graph_url + "/validation/normalForm." + format)
    self.assertEqual(requests.codes.ok, response.status_code)

  def test_get_random_nodes_degree(self):
    """Test GET /provapi/documents/random/{nodes}/{degree}.
    """
    response = requests.get(self.url + "random/1/1")
    self.assertEqual(requests.codes.ok, response.status_code)

  def test_get_random_nodes_degree_seed(self):
    """Test GET /provapi/documents/random/{nodes}/{degree}/{seed}.
    """
    response = requests.get(self.url + "random/1/2/3")
    self.assertEqual(requests.codes.ok, response.status_code)
