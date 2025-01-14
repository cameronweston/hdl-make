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

"""Module providing support for Xilinx Vivado simulation"""


from __future__ import absolute_import
from .makefilesim import MakefileSim
from .xilinx_prj import ToolXilinxProject
from ..util import shell


class ToolVivadoSim(ToolXilinxProject, MakefileSim):

    """Class providing the interface for Xilinx Vivado synthesis"""

    TOOL_INFO = {
        'name': 'vivado-sim',
        'id': 'vivado-sim',
        'windows_bin': 'vivado -mode batch -source',
        'linux_bin': 'vivado -mode batch -source',
    }

    STANDARD_LIBS = ['ieee', 'std']
    SYSTEM_LIBS = ['xilinx']

    CLEAN_TARGETS = {'clean': [".Xil", "*.jou", "*.log", "*.pb",
                               "work", "xsim.dir"],
                     'mrproper': ["*.wdb", "*.vcd"]}

    SIMULATOR_CONTROLS = {'vlog': 'xvlog $(XVLOG_OPT) $<',
                          'vhdl': 'xvhdl --work {work} $(XVHDL_OPT) $<',
                          'compiler': 'xelab -debug all $(TOP_MODULE) '
                                      '-s $(TOP_MODULE)'}

    def __init__(self):
        super(ToolVivadoSim, self).__init__()

    def _makefile_sim_project(self):
        """Generate a project file (to be used by vivado)"""
        self.writeln("project.tcl: Makefile")
        q = '' if shell.check_windows_commands() else '"'
        self.writeln("\t@echo {q}create_project -force $(TOP_MODULE)_prj ./{q} > $@".format(q=q))
        self.write_commands_project()
        self.writeln("\t@echo {q}exit{q} >> $@".format(q=q))
        self.writeln()
        self.writeln("project: project.tcl")
        self.writeln("\t{} $<".format(self.get_tool_bin()))
        self.writeln()

    def _makefile_sim_options(self):
        """Print the Vivado Sim options to the Makefile"""
        xvhdl_opt = self.manifest_dict.get("xvhdl_opt", '')
        self.writeln("XVHDL_OPT := {xvhdl_opt}\n".format(xvhdl_opt=xvhdl_opt))
        xvlog_opt = self.manifest_dict.get("xvlog_opt", '')
        self.writeln("XVLOG_OPT := {xvlog_opt}\n".format(xvlog_opt=xvlog_opt))

    def _makefile_sim_compilation(self):
        """Generate compile simulation Makefile target for Vivado Simulator"""
        libs = self.get_all_libs()
        self._makefile_sim_libs_variables(libs)
        self.writeln("simulation: $(VERILOG_OBJ) $(VHDL_OBJ)")
        self.writeln("\t\t" + self.SIMULATOR_CONTROLS['compiler'])
        self.writeln()
        self._makefile_sim_dep_files()
        self._makefile_sim_project()
