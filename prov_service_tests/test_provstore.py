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
  """Test class for ProvStore service. These tests check that
  ProvStore is available and responds to requests directed against its  
  `REST API <https://provenance.ecs.soton.ac.uk/store/help/api/>`_.

  The class expects two environment variables to be set:

  - ``PROVSTORE_URL`` - ProvStore base URL e.g.
    ``https://provenance.ecs.soton.ac.uk/store/api/v0/documents/``
  - ``PROVSTORE_API_KEY`` - ProvStore user name and API key e.g.
    ``user:12345qwert``
  """

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
    standards.JSON: "application/json"
  }
  """dict: mapping from formats in ``prov_service_tests.standards``
  to content types understood by ProvStore
  """

  EXTENSIONS = {standards.PROVX: "xml"}
  """dict: mapping from formats in ``prov_service_tests.standards`` to
  file extensions understood by ProvStore
` """

  def setUp(self):
    super(ProvStoreTestCase, self).setUp()
    self.url = os.environ[ProvStoreTestCase.URL_ENV]
    self.authorization = "ApiKey " + \
        os.environ[ProvStoreTestCase.API_KEY_ENV]
    self.document_url = None

  def tearDown(self):
    super(ProvStoreTestCase, self).tearDown()
    if self.document_url is not None:
      response = requests.delete( \
        self.document_url, 
        headers={http.AUTHORIZATION: self.authorization})
      if response.status_code != requests.codes.no_content:
        print("Warning: " + self.document_url + 
              " may not have been deleted")

  def post(self, document, format=standards.JSON):
    """Submit authorized POST /store/api/v0/documents/
    request. The document URL is cached by the class. A test is done
    to check that the response code is 201 CREATED.
    
    :param document: document in given format
    :type document: str or unicode
    :param format: one of ``prov_service_tests.standards`` formats
    :type format: str or unicode
    :return: URL of stored document
    :rtype: str or unicode
    """
    headers = {http.CONTENT_TYPE: ProvStoreTestCase.CONTENT_TYPES[format],
               http.ACCEPT: ProvStoreTestCase.CONTENT_TYPES[standards.JSON],
               http.AUTHORIZATION: self.authorization}
    request = {"content": document, 
               "public": True, 
               "rec_id": self.__class__.__name__}
    response = requests.post(self.url, 
                             headers=headers, 
                             data=json.dumps(request))
    self.assertEqual(requests.codes.created, response.status_code)
    response_json = json.loads(response.text)
    return self.url + str(response_json["id"])

  def test_get_documents(self):
    """Test GET /store/api/v0/documents/.
    """
    response = requests.get(self.url)
    self.assertEqual(requests.codes.ok, response.status_code)

  @parameterized.expand(standards.FORMATS)
  def test_post_document(self, format):
    """Test POST /store/api/v0/documents/.
    """
    self.document_url = self.post(self.get_primer(format), format)
    self.assertNotEqual(None, self.document_url)

  def test_delete_document(self):
    """Test DELETE /store/api/v0/documents/:id/.
    """
    self.document_url = self.post(self.get_primer(standards.JSON))

    headers = {http.AUTHORIZATION: self.authorization}
    response = requests.delete(self.document_url, headers=headers)
    self.assertEqual(requests.codes.no_content, response.status_code)
    self.document_url = None

  def test_get_document(self):
    """Test GET /store/api/v0/documents/:id/.
    """
    self.document_url = self.post(self.get_primer(standards.JSON))

    response = requests.get(self.document_url)
    self.assertEqual(requests.codes.ok, response.status_code)

  @parameterized.expand(standards.FORMATS)
  def test_get_document_format(self, format):
    """Test GET /store/api/v0/documents/:id.:format.
    """
    self.document_url = self.post(self.get_primer(standards.JSON))

    # Map format to extension supported by ProvStore
    if format in ProvStoreTestCase.EXTENSIONS:
      format = ProvStoreTestCase.EXTENSIONS[format]
    response = requests.get(self.document_url + "." + format)
    self.assertEqual(requests.codes.ok, response.status_code)

  def test_get_document_bundles(self):
    """Test GET /store/api/v0/documents/:id/bundles.
    """
    self.document_url = self.post(self.get_primer(standards.JSON))

    response = requests.get(self.document_url + "/bundles")
    self.assertEqual(requests.codes.ok, response.status_code)

  def post_bundle(self, document):
    """Submit GET /store/api/v0/documents/:doc_id/bundles/:bundle_id.

    Submit authorized POST /store/api/v0/documents/ request with
    a document that contains bundles and cache the document URL in
    the class, the bundles are then queried and the URL of the
    first bundle returned. Tests are done to check response codes and
    that at least one bundle is available.

    :param document: document in JSON format
    :type document: str or unicode
    :return: URL of bundle
    :rtype: str or unicode
    """
    self.document_url = self.post(document)

    response = requests.get(self.document_url + "/bundles")
    self.assertEqual(requests.codes.ok, response.status_code)    

    response_json = json.loads(response.text)
    objects = response_json["objects"]
    self.assertTrue(len(objects) > 0, msg="Expected at least one bundle")

    bundle_url = self.document_url + "/bundles/" + str(objects[0]["id"])
    response = requests.get(bundle_url)
    self.assertEqual(requests.codes.ok, response.status_code)
    return bundle_url

  def test_get_document_bundles_bundle(self):
    """Test GET /store/api/v0/documents/:doc_id/bundles/:bundle_id.
    """
    self.post_bundle(self.get_document("bundle.json"))

  @parameterized.expand(standards.FORMATS)
  def test_get_document_bundles_bundle_format(self, format):
    """Test GET /store/api/v0/documents/:doc_id/bundles/:bundle_id(.:format).
    """
    bundle_url = self.post_bundle(self.get_document("bundle.json"))

    # Map format to extension supported by ProvStore
    if format in ProvStoreTestCase.EXTENSIONS:
      format = ProvStoreTestCase.EXTENSIONS[format]
    response = requests.get(bundle_url + "." + format)
    self.assertEqual(requests.codes.ok, response.status_code)
