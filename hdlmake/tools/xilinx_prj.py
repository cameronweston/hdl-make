#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 - 2015 CERN
# Author: Pawel Szostek (pawel.szostek@cern.ch)
# Multi-tool support by Javier D. Garcia-Lasheras (javier@garcialasheras.com)
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
#

"""Module providing generic support for Xilinx projects"""


from __future__ import absolute_import
from ..sourcefiles.srcfile import VHDLFile, VerilogFile, SVFile, TCLFile
from ..util import shell


class ToolXilinxProject:

    _XILINX_ANY_SOURCE_PROPERTY = None

    # Commands to be executed to complete the addition of a source file
    # in the project (like setting the library)
    # Note: Ok to set_property LIBRARY work, previously done in vivado_sim. vivado(synth it was None, now work).
    _XILINX_VHDL_PROPERTY = (
        lambda srcfile: "set_property LIBRARY {library} [get_files {srcfile}]" if srcfile.library not in [None, "work"] else "")

    _XILINX_VERILOG_PROPERTY = ""

    # Dictionnary of commands per file type.
    HDL_FILES = {
        VHDLFile: _XILINX_VHDL_PROPERTY,
        VerilogFile: _XILINX_VERILOG_PROPERTY,
        SVFile: _XILINX_VERILOG_PROPERTY
    }

    SUPPORTED_FILES = {
        TCLFile: 'source {srcfile}'
    }

    def write_commands_project(self):
        """Write TCL commands (in a makefile) to populate a Xilinx project
            with the fileset
           Xilinx redefine the function as it adds files in batch
        """
        fileset_dict = {}
        fileset_dict.update(self.HDL_FILES)
        fileset_dict.update(self.SUPPORTED_FILES)
        # Add all files at once.
        self.writeln("\t@echo add_files -norecurse '{' >> $@")
        for srcfile in self.fileset.sort():
            if type(srcfile) in fileset_dict \
               and not isinstance(srcfile, TCLFile):
                self.writeln("\t@echo '{}' >> $@".format(
                    shell.tclpath(srcfile.rel_path())))
        self.writeln("\t@echo '}' >> $@")
        # Add per file properties (like library)
        self._makefile_syn_files_cmd(fileset_dict)
