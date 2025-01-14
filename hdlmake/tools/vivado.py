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

"""Module providing support for Xilinx Vivado synthesis"""


from __future__ import absolute_import
from .xilinx import ToolXilinx
from ..sourcefiles.srcfile import (VHDLFile, VerilogFile, SVFile,
                                   XDCFile, XCIFile, XCIXFile, NGCFile, XMPFile,
                                   XCOFile, COEFile, BDFile, TCLFile, BMMFile,
                                   MIFFile, RAMFile, VHOFile, VEOFile, XCFFile)


class ToolVivado(ToolXilinx):

    """Class providing the interface for Xilinx Vivado synthesis"""

    TOOL_INFO = {
        'name': 'vivado',
        'id': 'vivado',
        'windows_bin': 'vivado -mode batch -source',
        'linux_bin': 'vivado -mode batch -source',
        'project_ext': 'xpr'
    }

    STANDARD_LIBS = ['ieee', 'std']
    SYSTEM_LIBS = ['xilinx']

    SUPPORTED_FILES = {
         XDCFile: ToolXilinx._XILINX_ANY_SOURCE_PROPERTY,
         XCFFile: ToolXilinx._XILINX_ANY_SOURCE_PROPERTY,
         NGCFile: ToolXilinx._XILINX_ANY_SOURCE_PROPERTY,
         XMPFile: ToolXilinx._XILINX_ANY_SOURCE_PROPERTY,
         XCOFile: ToolXilinx._XILINX_ANY_SOURCE_PROPERTY,
         COEFile: ToolXilinx._XILINX_ANY_SOURCE_PROPERTY,
         BMMFile: ToolXilinx._XILINX_ANY_SOURCE_PROPERTY,
         TCLFile: ToolXilinx._XILINX_ANY_SOURCE_PROPERTY,
         MIFFile: ToolXilinx._XILINX_ANY_SOURCE_PROPERTY,
         RAMFile: ToolXilinx._XILINX_ANY_SOURCE_PROPERTY,
         VHOFile: ToolXilinx._XILINX_ANY_SOURCE_PROPERTY,
         VEOFile: ToolXilinx._XILINX_ANY_SOURCE_PROPERTY}
    SUPPORTED_FILES.update(ToolXilinx.SUPPORTED_FILES)

    HDL_FILES = {
        VHDLFile:    ToolXilinx._XILINX_VHDL_PROPERTY,
        VerilogFile: ToolXilinx._XILINX_VERILOG_PROPERTY,
        SVFile:      ToolXilinx._XILINX_VERILOG_PROPERTY,
        NGCFile:     ToolXilinx._XILINX_ANY_SOURCE_PROPERTY,
        XCIFile:     ToolXilinx._XILINX_ANY_SOURCE_PROPERTY,
        XCIXFile:     ToolXilinx._XILINX_ANY_SOURCE_PROPERTY,
        BDFile:      ToolXilinx._XILINX_ANY_SOURCE_PROPERTY}

    CLEAN_TARGETS = {'clean': [".Xil", "*.jou", "*.log", "*.pb", "*.dmp", "*.xsa",
                               "$(PROJECT).cache", "$(PROJECT).data", "work",
                               "$(PROJECT).runs", "$(PROJECT).hw",
                               "$(PROJECT).sim", "$(PROJECT).gen",
                               "$(PROJECT).ip_user_files", "$(PROJECT).srcs",
                               "$(PROJECT_FILE)"]}
    CLEAN_TARGETS.update(ToolXilinx.CLEAN_TARGETS)

    TCL_CONTROLS = {'bitstream': '$(TCL_OPEN)\n'
                                 'launch_runs impl_1 -to_step write_bitstream\n'
                                 'wait_on_run impl_1\n'
                                 '$(TCL_CLOSE)',
                    'prom': '$(TCL_OPEN)\n'
                                 'write_hw_platform -fixed -force -include_bit -file $(PROJECT).xsa\n'
                                 '$(TCL_CLOSE)'}

    def __init__(self):
        super(ToolVivado, self).__init__()
        self._tcl_controls.update(ToolVivado.TCL_CONTROLS)
