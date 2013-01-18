#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
## \package test nexdatas
## \file DBFieldTagWriterTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random

from pni.nx.h5 import open_file
from  xml.sax import SAXParseException


from ndts import TangoDataWriter, Types
from ndts.TangoDataWriter  import TangoDataWriter 
from Checkers import Checker

## test fixture
class DBFieldTagWriterTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._counter =  [1,-2,6,-8,9,-11]
        self._fcounter =  [1.1,-2.4,6.54,-8.456,9.456,-0.46545]
        self._sc = Checker(self)
        self._mca1 = [[random.randint(-100, 100) for e in range(256)] for i in range(3)]
        self._mca2 = [[random.randint(0, 100) for e in range(256)] for i in range(3)]
        self._fmca1 = [self._sc.nicePlot(1024, 10) for i in range(4)]
#        self._fmca2 = [(float(e)/(100.+e)) for e in range(2048)]
        self._pco1 = [[[random.randint(0, 100) for e1 in range(8)]  for e2 in range(10)] for i in range(3)]
        self._fpco1 = [self._sc.nicePlot2D(20, 30, 5) for i in range(4)]

    ## test starter
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."

    ## opens writer
    # \param fname file name     
    # \param xml XML settings
    # \returns Tango Data Writer instance   
    def openWriter(self, fname, xml, json = None):
        tdw = TangoDataWriter(fname)
        tdw.openNXFile()
        tdw.xmlSettings = xml
        if json:
            tdw.json = json
        tdw.openEntry()
        return tdw

    ## closes writer
    # \param tdw Tango Data Writer instance
    def closeWriter(self, tdw, json = None):
        if json:
            tdw.json = json
        tdw.closeEntry()
        tdw.closeNXFile()

    ## performs one record step
    def record(self, tdw, string):
        tdw.record(string)

    ## scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientIntScalar(self):
        print "Run: %s.test_dbIntScalar() " % self.__class__.__name__
        fname= '%s/dbintscalar.h5' % os.getcwd()   
        xml= """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">

        <field name="single_mysql_record_string" type="NX_CHAR">
          <dimensions rank="1">
            <dim index="1" value="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_string" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="haso228k.desy.de"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>
        <field name="single_mysql_record_int" type="NX_INT">
          <dimensions rank="1">
            <dim index="1" value="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="haso228k.desy.de"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>
        <field name="mysql_record" type="NX_CHAR">
          <dimensions rank="2">
            <dim index="1" value="10"/>
            <dim index="2" value="2"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="haso228k.desy.de"/>
            <query format="IMAGE">
              SELECT name, pid FROM device limit 10
            </query>
          </datasource>
        </field>
      </group>
    </group>
  </group>
</definition>
"""

        tdw = self.openWriter(fname, xml)

        for c in self._counter:
            self.record(tdw,'{ }')

        self.closeWriter(tdw)
        
        # check the created file
        
        f = open_file(fname,readonly=True)
        det = self._sc.checkScalarTree(f, fname , 22)
#        self._sc.checkScalarField(det, "counter", "int64", "NX_INT", self._counter)
       
        f.close()
#        os.remove(fname)



if __name__ == '__main__':
    unittest.main()
