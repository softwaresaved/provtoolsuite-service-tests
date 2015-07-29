"""Base class for service tests.
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

import inspect
import os
import requests
import tempfile
import unittest
from nose.tools import istest
from nose.tools import nottest
from nose_parameterized import parameterized

from prov_service_tests import standards

@nottest
class ServiceTestCase(unittest.TestCase):

  def setUp(self):
    super(ServiceTestCase, self).setUp()

  PRIMER_DOCUMENTS = {
    standards.PROVN: "primer.provn",
    standards.TTL: "primer.ttl",
    standards.TRIG: "primer.trig",
    standards.PROVX: "primer.provx",
    standards.JSON: "primer.json"
  }
  """dict: mapping :mod:`prov_service_tests.standards` values
     to `primer.*` files
  """

  def get_document(self, file_name):
    """Load a document from a file relative to a ``documents``
    directory assumed to be in the same directory as the caller.

    :param file_name: file name
    :type file_name: str or unicode
    :return: document
    :rtype: str or unicode
    :raises OSError: 
      if there are problems accessing the directory or loading the file
    """
    directory = os.path.join(
      os.path.dirname(os.path.abspath(inspect.getfile(
            inspect.currentframe()))), "documents")
    with open(os.path.join(directory, file_name), "r") as f:
          return f.read()

  def get_primer(self, format):
    """Load document a from a ``primer.format`` file within a 
    ``documents`` directory assumed to be in the same directory as the
    caller.

    :param format: a :mod:`prov_service_tests.standards` value
    :type format: str or unicode
    :return: document
    :rtype: str or unicode
    :raise: OSError: 
      if there are problems accessing the directory or loading the file
    """
    return self.get_document(ServiceTestCase.PRIMER_DOCUMENTS[format])
