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

  URL_ENV = "PROVVALIDATOR_URL"
  """str or unicode: environment variable holding ProvValidator URL
  """

  CONTENT_TYPES = {
    standards.PROVN: "text/provenance-notation",
    standards.TTL: "text/turtle",
    standards.TRIG: "application/trig",
    standards.PROVX: "application/provenance+xml",
    standards.JSON: "application/json"}
  """dict: mapping from formats in ``prov_service_tests.standards`` to
    content types """

  def setUp(self):
    super(ProvValidatorTestCase, self).setUp()
    self.url = os.environ[ProvValidatorTestCase.URL_ENV]

  def tearDown(self):
    super(ProvValidatorTestCase, self).tearDown()

  @parameterized.expand(standards.FORMATS)
  def test_validate(self, format):
    document = self.get_primer(format)
    headers = {http.ACCEPT: "text/html"}
    files = {"statements": document}
    data = {"validate": "Validate", "type": format}
    response = requests.post(self.url, 
                             headers=headers, 
                             files=files, 
                             data=data)
    self.assertEqual(requests.codes.ok, response.status_code) # 200 OK

  @parameterized.expand(standards.FORMATS)
  def test_simple_translate(self, format):
    document = self.get_primer(format)
    content_type = ProvValidatorTestCase.CONTENT_TYPES[format]
    accept_type = ProvValidatorTestCase.CONTENT_TYPES[format]
    headers = {http.CONTENT_TYPE: content_type, 
               http.ACCEPT: accept_type}
    response = requests.post(self.url, 
                             headers=headers, 
                             data=document)
    self.assertEqual(requests.codes.ok, response.status_code) # 200 OK

  @parameterized.expand(standards.FORMATS)
  def test_simple_translate_no_redirect(self, format):
    document = self.get_primer(format)
    content_type = ProvValidatorTestCase.CONTENT_TYPES[format]
    accept_type = ProvValidatorTestCase.CONTENT_TYPES[format]
    headers = {http.CONTENT_TYPE: content_type, 
               http.ACCEPT: accept_type}
    # POST /provapi/documents/
    response = requests.post(self.url, 
                             headers=headers, 
                             allow_redirects=False,
                             data=document)
    self.assertEqual(requests.codes.see_other, 
                     response.status_code) # 303 See Other
    doc_url = response.headers["location"]
    response = requests.get(doc_url, 
                            headers=headers, 
                            allow_redirects=False)
    self.assertEqual(requests.codes.see_other, 
                     response.status_code) # 303 See Other
    # GET /provapi/documents/{docId}
    response = requests.get(response.headers["location"], 
                            headers=headers, 
                            allow_redirects=False)
    self.assertEqual(requests.codes.ok, response.status_code) # 200 OK
    # GET /provapi/documents/{docId}.{type}
    response = requests.get(doc_url + "." + format, 
                            allow_redirects=False)
    self.assertEqual(requests.codes.ok, response.status_code) # 200 OK

    # GET /provapi/documents/{docId}/metrics
    response = requests.get(doc_url + "/metrics", 
                            allow_redirects=False)
    print(response.headers)
#    self.assertEqual(requests.codes.ok, response.status_code) # 200 OK

    # GET /provapi/documents/{docId}/original
    response = requests.get(doc_url + "/original", 
                            allow_redirects=False)
    self.assertEqual(requests.codes.ok, response.status_code) # 200 OK



# For VALIDATOR - combine these into a single file!!!
# Remove services.*

    # GET /provapi/documents/{docId}/validation/matrix
#    response = requests.get(doc_url + "/validation/matrix", 
#                            headers={http.ACCEPT: "text/plain"},
#                            allow_redirects=False)
#    self.assertEqual(requests.codes.see_other, 
#                     response.status_code) # 303 See Other
#    print(response.headers["location"])

#    response = requests.get(doc_url + "/validation/matrix", 
#                            headers={http.ACCEPT: "image/png"},
#                            allow_redirects=False)
#    self.assertEqual(requests.codes.see_other, 
#                     response.status_code) # 303 See Other
#    print(response.headers["location"])


#    print(response.headers)
#    print(response.text)
#    url = response.headers["location"]
#    print(url)
#    response = requests.get(url, 
                            #                            headers=headers, 
#                            allow_redirects=False)
#    print(response.headers)
#    self.assertEqual(requests.codes.ok, response.status_code) # 200 OK


# /metrics
# - no content

#GET /provapi/documents/{docId}/validation/matrix Event Matrix
# Accept text/plain, image/png
#GET /provapi/documents/{docId}/validation/matrix.png Event Matrix -- Image Representation
#GET /provapi/documents/{docId}/validation/matrix.txt Event Matrix -- Text Representation
#GET /provapi/documents/{docId}/validation/matrix/diagonal Event Matrix Diagonal
#GET /provapi/documents/{docId}/validation/normalForm Document in normal form
  # Accept one of the usual PROV content ypes
#GET /provapi/documents/{docId}/validation/normalForm.{type} Normal form of a document into given representation
 # One of the usual PROV extensions
#GET /provapi/documents/{docId}/validation/report Validation Report
# Accept text/html text/html application/xml
#GET /provapi/documents/{docId}/validation/report.xml Validation Report -- XML representation
#GET /provapi/documents/{docId}/validation/report/{part} Validation Report Component
 # Part = ??? to ???
#GET /provapi/documents/{docId}/vis/gantt Visualization: gantt plot
#GET /provapi/documents/{docId}/vis/hive Visualization: hive plot
#GET /provapi/documents/{docId}/vis/wheel Visualization: wheel plot
#GET /provapi/documents/random/{nodes}/{degree} Randomly generated Document
  # nodes and degree are ints
  # Accept is the content types
#GET /provapi/documents/random/{nodes}/{degree}/{seed} Randomly generated Document
  # nodes and degree are ints
  # seeds is long
  # Accept is the content types

#/ptm Show/Hide List Operations Expand Operations Raw
# ...
