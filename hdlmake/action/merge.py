#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 CERN
# Author: Pawel Szostek (pawel.szostek@cern.ch)
#
# This file is part of Hdlmake.
#
# Hdlmake is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hdlmake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hdlmake.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import logging
import os
import os.path
import time
import sys

from hdlmake.srcfile import VerilogFile, VHDLFile, NGCFile
from hdlmake.vlog_parser import VerilogPreprocessor

from .action import Action


class ActionMerge(Action):

    def merge_cores(self):
        self._check_all_fetched_or_quit()
        logging.info("Merging all cores into one source file per language.")
        flist = self.build_file_set()
        base = self.env.options.dest

        file_header = (
            "\n\n\n\n"
            "------------------------------ WARNING -------------------------------\n"
            "-- This code has been generated by hdlmake --merge-cores option     --\n"
            "-- It is provided for your convenience, to spare you from adding    --\n"
            "-- lots of individual source files to ISE/Modelsim/Quartus projects --\n"
            "-- mainly for Windows users. Please DO NOT MODIFY this file. If you --\n"
            "-- need to change something inside, edit the original source file   --\n"
            "-- and re-genrate the merged version!                               --\n"
            "----------------------------------------------------------------------\n"
            "\n\n\n\n"
            ) 

        # Generate a VHDL file containing all the required VHDL files
        f_out = open(base+".vhd", "w")
        f_out.write(file_header)
        for vhdl in flist.filter(VHDLFile):
            f_out.write("\n\n---  File: %s ----\n" % vhdl.rel_path())
            f_out.write("---  Source: %s\n" % vhdl.module.url)
            if vhdl.module.revision:
                f_out.write("---  Revision: %s\n" % vhdl.module.revision)
            f_out.write("---  Last modified: %s\n" % time.ctime(os.path.getmtime(vhdl.path)))
            f_out.write(open(vhdl.rel_path(), "r").read()+"\n\n")
                #print("VHDL: %s" % vhdl.rel_path())
        f_out.close()

        # Generate a VHDL file containing all the required VHDL files
        f_out = open(base+".v", "w")
        f_out.write(file_header)
        for vlog in flist.filter(VerilogFile):
            f_out.write("\n\n//  File: %s\n" % vlog.rel_path())
            f_out.write("//  Source: %s\n" % vlog.module.url)
            if vlog.module.revision:
                f_out.write("//  Revision: %s\n" % vlog.module.revision)
            f_out.write("//  Last modified: %s\n" % time.ctime(os.path.getmtime(vlog.path)))
            vpp = VerilogPreprocessor()
            for include_path in vlog.include_dirs:
                vpp.add_path(include_path)
            vpp.add_path(vlog.dirname)
            f_out.write(vpp.preprocess(vlog.rel_path()))
        f_out.close()

        # Handling NGC files
        current_path = os.getcwd()
        for ngc in flist.filter(NGCFile):
            import shutil
            logging.info("copying NGC file: %s" % ngc.rel_path())
            shutil.copy(ngc.rel_path(), current_path)

        logging.info("Cores merged.")