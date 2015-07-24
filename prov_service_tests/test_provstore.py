"""Test class for ProvStore service``.
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
class ProvStoreTestCase(ServiceTestCase):

  URL_ENV = "PROVSTORE_URL"
  """str or unicode: environment variable holding ProvStore URL
  """

  API_KEY_ENV = "PROVSTORE_API_KEY"
  """str or unicode: environment variable holding ProvStore API
  key
  """

  CONTENT_TYPES = {
    standards.PROVN: "text/provenance-notation",
    standards.TTL: "text/turtle",
    standards.TRIG: "application/trig",
    standards.PROVX: "application/xml",
    standards.JSON: "application/json"}
  """dict: mapping from formats in ``prov_service_tests..standards``
  to content types 
  """

  def setUp(self):
    super(ProvStoreTestCase, self).setUp()
    self.url = os.environ[ProvStoreTestCase.URL_ENV]
    self.authorization = "ApiKey " + os.environ[ProvStoreTestCase.API_KEY_ENV]

  def tearDown(self):
    super(ProvStoreTestCase, self).tearDown()

  @parameterized.expand(standards.FORMATS)
  def test_store(self, format):
    document = self.get_document(format)
    content_type = ProvStoreTestCase.CONTENT_TYPES[format]
    accept_type = ProvStoreTestCase.CONTENT_TYPES[standards.JSON]
    headers = {http.CONTENT_TYPE: content_type, 
               http.ACCEPT: accept_type,
               http.AUTHORIZATION: self.authorization}
    store_request = {"content": document, 
                     "public": True, 
                     "rec_id": self.__class__.__name__}
    response = requests.post(self.url, 
                             headers=headers, 
                             data=json.dumps(store_request))
    self.assertEqual(requests.codes.created, 
                     response.status_code) # 201 CREATED
    
    response_json = json.loads(response.text)
    document_id = response_json["id"]
    document_url = self.url + str(document_id)
    accept_type = ProvStoreTestCase.CONTENT_TYPES[format]
    headers = {http.ACCEPT: accept_type}
    response = requests.get(document_url + "." + format, 
                            headers=headers, 
                            allow_redirects=True)
    self.assertEqual(requests.codes.ok, 
                     response.status_code) # 200 OK

    headers = {http.AUTHORIZATION: self.authorization}
    response = requests.delete(document_url, headers=headers)
    self.assertEqual(requests.codes.no_content, 
                     response.status_code) # 204 NO CONTENT
