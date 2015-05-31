#!/usr/bin/env python
# Copyright (c) 2014 Daniel Kraft
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# RPC test for the name scanning functions (name_scan and name_filter).

from test_framework.names import NameTestFramework
from test_framework.util import *

class NameScanningTest (NameTestFramework):

  def run_test (self):
    NameTestFramework.run_test (self)

    # It would also nice to test the "initial download" error,
    # but it will only pop up if the blockchain directory (in the cache)
    # is old enough.  This can not be guaranteed (if the cache is freshly
    # generated), so that we cannot use it as a "strict" test here.
    # Instead, only warn if the test "fails".

    initialDownloadOk = True

    try:
      self.nodes[0].name_show ("a")
      initialDownloadOk = False
    except JSONRPCException as exc:
      if exc.error['code'] != -10:
        initialDownloadOk = False
    try:
      self.nodes[1].name_history ("a")
      initialDownloadOk = False
    except JSONRPCException as exc:
      if exc.error['code'] != -10:
        initialDownloadOk = False
    try:
      self.nodes[0].name_scan ()
      initialDownloadOk = False
    except JSONRPCException as exc:
      if exc.error['code'] != -10:
        initialDownloadOk = False
    try:
      self.nodes[0].name_filter ()
      initialDownloadOk = False
    except JSONRPCException as exc:
      if exc.error['code'] != -10:
        initialDownloadOk = False

    if not initialDownloadOk:
      print "WARNING: 'initial blockchain download' check failed!"
      print ("This probably means that the blockchain was regenerated"
              + " and is fine.")

    # Mine a block so that we're no longer in initial download.
    self.generate (3, 1)

    # Initially, all should be empty.
    assert_equal (self.nodes[0].name_scan (), [])
    assert_equal (self.nodes[0].name_scan ("foo", 10), [])
    assert_equal (self.nodes[0].name_filter (), [])
    assert_equal (self.nodes[0].name_filter ("", 0, 0, 0, "stat"),
                  {"blocks": 201,"count": 0})

    # Register some names with various data, heights and expiration status.
    # Using both "aa" and "b" ensures that we can also check for the expected
    # comparison order between string length and lexicographic ordering.

    newA = self.nodes[0].name_new ("a")
    newAA = self.nodes[0].name_new ("aa")
    newB = self.nodes[1].name_new ("b")
    newC = self.nodes[2].name_new ("c")
    self.generate (3, 15)

    self.firstupdateName (0, "a", newA, "wrong value")
    self.firstupdateName (0, "aa", newAA, "value aa")
    self.firstupdateName (1, "b", newB, "value b")
    self.generate (3, 15)
    self.firstupdateName (2, "c", newC, "value c")
    self.nodes[0].name_update ("a", "value a")
    self.generate (3, 20)

    # Check the expected name_scan data values.
    scan = self.nodes[3].name_scan ()
    assert_equal (len (scan), 4)
    self.checkNameData (scan[0], "a", "value a", 11, False)
    self.checkNameData (scan[1], "b", "value b", -4, True)
    self.checkNameData (scan[2], "c", "value c", 11, False)
    self.checkNameData (scan[3], "aa", "value aa", -4, True)

    # Check for expected names in various name_scan calls.
    self.checkList (self.nodes[3].name_scan (), ["a", "b", "c", "aa"])
    self.checkList (self.nodes[3].name_scan ("", 0), [])
    self.checkList (self.nodes[3].name_scan ("", -1), [])
    self.checkList (self.nodes[3].name_scan ("b"), ["b", "c", "aa"])
    self.checkList (self.nodes[3].name_scan ("zz"), [])
    self.checkList (self.nodes[3].name_scan ("", 2), ["a", "b"])
    self.checkList (self.nodes[3].name_scan ("b", 1), ["b"])

    # Check the expected name_filter data values.
    scan = self.nodes[3].name_scan ()
    assert_equal (len (scan), 4)
    self.checkNameData (scan[0], "a", "value a", 11, False)
    self.checkNameData (scan[1], "b", "value b", -4, True)
    self.checkNameData (scan[2], "c", "value c", 11, False)
    self.checkNameData (scan[3], "aa", "value aa", -4, True)

    # Check for expected names in various name_filter calls.
    height = self.nodes[3].getblockcount ()
    self.checkList (self.nodes[3].name_filter (), ["a", "b", "c", "aa"])
    self.checkList (self.nodes[3].name_filter ("[ac]"), ["a", "c", "aa"])
    self.checkList (self.nodes[3].name_filter ("", 10), [])
    self.checkList (self.nodes[3].name_filter ("", 30), ["a", "c"])
    self.checkList (self.nodes[3].name_filter ("", 0, 0, 0),
                    ["a", "b", "c", "aa"])
    self.checkList (self.nodes[3].name_filter ("", 0, 0, 1), ["a"])
    self.checkList (self.nodes[3].name_filter ("", 0, 1, 4), ["b", "c", "aa"])
    self.checkList (self.nodes[3].name_filter ("", 0, 4, 4), [])
    assert_equal (self.nodes[3].name_filter ("", 30, 0, 0, "stat"),
                  {"blocks": height, "count": 2})

    # Check test for "stat" argument.
    try:
      self.nodes[3].name_filter ("", 0, 0, 0, "string")
      raise AssertionError ("wrong check for 'stat' argument")
    except JSONRPCException as exc:
      assert_equal (exc.error['code'], -8)

  def checkList (self, data, names):
    """
    Check that the result in 'data' contains the names
    given in the array 'names'.
    """

    def walker (e):
      return e['name']
    dataNames = map (walker, data)

    assert_equal (dataNames, names)

if __name__ == '__main__':
  NameScanningTest ().main ()
