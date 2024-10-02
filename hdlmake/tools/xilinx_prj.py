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
from ..sourcefiles.srcfile import VHDLFile, VerilogFile, SVFile, TCLFile, SourceFile
from ..util import shell


class ToolXilinxProject:

    _XILINX_ANY_SOURCE_PROPERTY = None

    # Commands to be executed to complete the addition of a source file
    # in the project (like setting the library)
    _XILINX_VHDL_PROPERTY = (
        lambda property_str: 'set_property -dict "{property_str}" [get_files {srcfile}]' if property_str is not "" else '')

    _XILINX_VERILOG_PROPERTY = (
        lambda property_str: 'set_property -dict "{property_str}" [get_files {srcfile}]' if property_str is not "" else '')

    _XILINX_TCL_PROPERTY = (
        lambda property_str: 'source {srcfile}; set_property -dict "{property_str}" [get_files {srcfile}]' if property_str is not "" else 'source {srcfile}')

    # Dictionnary of commands per file type.
    HDL_FILES = {
        VHDLFile: _XILINX_VHDL_PROPERTY,
        VerilogFile: _XILINX_VERILOG_PROPERTY,
        SVFile: _XILINX_VERILOG_PROPERTY
    }

    SUPPORTED_FILES = {
        TCLFile: _XILINX_TCL_PROPERTY
    }

    def write_commands_project(self):
        """Write TCL commands (in a makefile) to populate a Xilinx project
            with the fileset
        """
        fileset_dict = {}
        fileset_dict.update(self.HDL_FILES)
        fileset_dict.update(self.SUPPORTED_FILES)
        # Add all files at once.
        self.writeln("\t@echo add_files -norecurse '{' >> $@")
        for srcfile in self.fileset.sort():
            if type(srcfile) in fileset_dict:
                self.writeln("\t@echo '{}' >> $@".format(
                    shell.tclpath(srcfile.rel_path())))
        self.writeln("\t@echo '}' >> $@")
        # Grab vhdl version info
        src_properties = self.manifest_dict.get('src_properties', [])
        # Add per file properties (like library)
        for srcfile in self.fileset.sort():
            property_str = ""
            command = fileset_dict.get(type(srcfile))
            # Put the file in files.tcl only if it is supported.
            if command is not None:
                self._all_sources.append(srcfile.rel_path())
                # Libraries are defined only for hdl files.
                if isinstance(srcfile, SourceFile):
                    library = srcfile.library
                    property_str = f"LIBRARY {library}" if library not in [None, "work"] else ""
                else:
                    library = None
                # Handle vhdl specific properties
                if isinstance(srcfile, VHDLFile):
                    property_str += f" {src_properties['vhdl']}" if 'vhdl' in src_properties else ""
                elif isinstance(srcfile, VerilogFile):
                    property_str += f" {src_properties['verilog']}" if 'verilog' in src_properties else ""
                elif isinstance(srcfile, TCLFile):
                    property_str += f" {src_properties['tcl']}" if 'tcl' in src_properties else ""

                if callable(command):
                    command = command(property_str)
                cmd = command.format(srcfile=shell.tclpath(srcfile.rel_path()),
                                     property_str=property_str)
                if cmd:
                    self.writeln("\t@echo '{}' >> $@".format(cmd))
