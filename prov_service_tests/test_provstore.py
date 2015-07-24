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
  """dict: mapping from formats in ``prov_service_tests..standards``
  to content types 
  """

  def setUp(self):
    super(ProvStoreTestCase, self).setUp()
    self.url = os.environ[ProvStoreTestCase.URL_ENV]
    self.authorization = "ApiKey " + os.environ[ProvStoreTestCase.API_KEY_ENV]
    self.document_url = None

  def tearDown(self):
    super(ProvStoreTestCase, self).tearDown()
    if self.document_url is not None:
      try:
        response = requests.delete( \
          self.document_url, 
          headers={http.AUTHORIZATION: self.authorization})
        if (response.status_code != requests.codes.no_content):
          self.delete_document_warning()
      except Exception as exception:
        self.delete_document_warning()

  def delete_document_warning(self):
    """Print a warning that a document could not be deleted.
    """
    print("Warning: " + self.document_url + " could not be deleted")

  def post(self, url, content_type, accept_type, request):
    """Submit authorized POST request and return response.

    :param url: URL
    :type url: str or unicode
    :param content_type: Content-type value
    :type content_type: str or unicode
    :param accept_type: Accept value
    :type accept_type: str or unicode
    :param request: request
    :type request: dict
    :return: response
    :rtype: :class:`~requests.Response``
    """
    headers = {http.CONTENT_TYPE: content_type, 
               http.ACCEPT: accept_type,
               http.AUTHORIZATION: self.authorization}
    return requests.post(url, 
                         headers=headers, 
                         data=json.dumps(request))

  def post_document(self, format, document):
    """Submit authorized POST /store/api/v0/documents/
    request. The document URL is cached by the class. A test is done
    to check that the response code is 201 CREATED.

    :param format: one of ``prov_service_tests.standards`` formats
    :type format: str or unicode
    :param document: document in given format
    :type document: str or unicode
    :return: response
    :rtype: :class:`~requests.Response``
    """
    store_request = {"content": document, 
                     "public": True, 
                     "rec_id": self.__class__.__name__}
    response = self.post(self.url,
                         ProvStoreTestCase.CONTENT_TYPES[format],
                         ProvStoreTestCase.CONTENT_TYPES[standards.JSON],
                         store_request)
    self.assertEqual(requests.codes.created, response.status_code)
    response_json = json.loads(response.text)
    self.document_url = self.url + str(response_json["id"])
    return response

  def test_get_documents(self):
    """Test GET /store/api/v0/documents/.
    """
    response = requests.get(self.url)
    self.assertEqual(requests.codes.ok, response.status_code)

  @parameterized.expand(standards.FORMATS)
  def test_post_document(self, format):
    """Test POST /store/api/v0/documents/.
    """
    response = self.post_document(format, self.get_primer(format))
    self.assertNotEqual(None, self.document_url)

  def test_delete_document(self):
    """Test DELETE /store/api/v0/documents/:id/.
    """
    format = standards.JSON
    response = self.post_document(format, self.get_primer(format))

    response = requests.delete( \
      self.document_url, 
      headers={http.AUTHORIZATION: self.authorization})
    self.assertEqual(requests.codes.no_content, response.status_code)
    self.document_url = None

  def test_get_document(self):
    """GET /store/api/v0/documents/:id/.
    """
    format = standards.JSON
    response = self.post_document(format, self.get_primer(format))

    response = requests.get(self.document_url)
    self.assertEqual(requests.codes.ok, response.status_code)

  @parameterized.expand(standards.FORMATS)
  def test_get_document_format(self, format):
    """GET /store/api/v0/documents/:id.:format, 
    """
    response = self.post_document(format, self.get_primer(format))
    # Get document in each format.
    for get_format in standards.FORMATS:
      response = requests.get( \
        self.document_url + "." + get_format, 
        headers={http.ACCEPT: ProvStoreTestCase.CONTENT_TYPES[get_format]})
      self.assertEqual(requests.codes.ok, response.status_code)

  def test_get_document_bundles(self):
    """GET /store/api/v0/documents/:id/bundles 
    """
    format = standards.JSON
    response = self.post_document(format, self.get_primer(format))
    response = requests.get(self.document_url + "/bundles")
    self.assertEqual(requests.codes.ok, response.status_code)

  def test_get_document_bundles_bundle_format(self):
    """GET /store/api/v0/documents/:doc_id/bundles/:bundle_id(.:format)
    """
    format = standards.JSON
    response = self.post_document(format, self.get_document("bundle.json"))

    response = requests.get(self.document_url + "/bundles")
    self.assertEqual(requests.codes.ok, response.status_code)    

    response_json = json.loads(response.text)
    objects = response_json["objects"]
    self.assertTrue(len(objects) > 0)
    bundle_id = objects[0]["id"]
    bundle_url = self.document_url + "/bundles/" + str(bundle_id)
    response = requests.get(bundle_url)
    self.assertEqual(requests.codes.ok, response.status_code)
    # Get bundle in each format.
    for bundle_format in standards.FORMATS:
      response = requests.get( \
        bundle_url + "." + bundle_format,
        headers={http.ACCEPT: ProvStoreTestCase.CONTENT_TYPES[bundle_format]})
      self.assertEqual(requests.codes.ok, response.status_code)
