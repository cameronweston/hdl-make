#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Cameron Weston (cameronweston@duck.com)
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

"""Module providing support for Lattice Radiant IDE"""


from __future__ import absolute_import
from .makefilesyn import MakefileSyn
from ..sourcefiles.srcfile import VHDLFile, VerilogFile, IPXFile, RVLFile, RVAFile, PDCFile, SDCFile, STYFile


class ToolRadiant(MakefileSyn):

    """Class providing the interface for Lattice Radiant synthesis"""

    TOOL_INFO = {
        'name': 'Radiant',
        'id': 'radiant',
        'windows_bin': 'pnmainc.exe',
        'linux_bin': 'radiantc',
        'project_ext': 'rdf'}

    STANDARD_LIBS = ['ieee', 'std']

    _LATTICE_SOURCE = 'prj_add_source {{srcfile}}'
    _LATTICE_HDL = 'prj_add_source {{srcfile}} -work {{library}}'
    _LATTICE_STRATEGY = 'prj_import_strategy -name $(PROJECT) -file {{srcfile}}; prj_set_strategy $(PROJECT)'
    _LATTICE_PURGE_SOURCE = 'prj_remove_source -all'

    SUPPORTED_FILES = {
        IPXFile: _LATTICE_SOURCE.format(''),
        RVLFile: _LATTICE_SOURCE.format(''),
        RVAFile: _LATTICE_SOURCE.format(''),
        PDCFile: _LATTICE_SOURCE.format(''),
        SDCFile: _LATTICE_SOURCE.format(''),
        STYFile: _LATTICE_STRATEGY.format('')
        }

    HDL_FILES = {
        VHDLFile: _LATTICE_HDL.format(''),
        VerilogFile: _LATTICE_HDL.format('')}

    CLEAN_TARGETS = {'clean': ["*.sty", "*.rdf", "impl1", "*.xml", "*.ini", "*.html", "*.dir"],
                     'mrproper': ["*.bit"]}

    TCL_CONTROLS = {'create': 'prj_create -name $(PROJECT)'
                              ' -impl impl1'
                              ' -dev {0} -performance {1} -synthesis \"synplify\"',
                    'open': 'prj_open $(PROJECT).rdf',
                    'save': 'prj_save',
                    'close': 'prj_close',
                    'project': '$(TCL_CREATE)\n'
                               'source files.tcl\n'
                               '$(TCL_SAVE)\n'
                               '$(TCL_CLOSE)',
                    'par': '$(TCL_OPEN)\n'
                           'prj_run_par\n'
                           '$(TCL_SAVE)\n'
                           '$(TCL_CLOSE)',
                    'bitstream': '$(TCL_OPEN)\n'
                                 'prj_run Export -impl impl1\n'
                                 '$(TCL_SAVE)\n'
                                 '$(TCL_CLOSE)',
                    'files': _LATTICE_PURGE_SOURCE}

    def __init__(self):
        super(ToolRadiant, self).__init__()
        self._tcl_controls.update(ToolRadiant.TCL_CONTROLS)

    def _makefile_syn_tcl(self):
        """Create a Radiant synthesis project by TCL"""
        syn_device = self.manifest_dict["syn_device"]
        syn_grade = self.manifest_dict["syn_grade"]
        syn_package = self.manifest_dict["syn_package"]
        create_tmp = self._tcl_controls["create"]
        target = syn_device + '-' + syn_grade[0] + syn_package
        grade = syn_grade
        self._tcl_controls["create"] = create_tmp.format(target.upper(), grade)
        super(ToolRadiant, self)._makefile_syn_tcl()

    def _makefile_syn_files_map_files_to_lib(self):
        '''Hijacking this function to handle strategy options after adding strategy'''
        strategy_opt = self.manifest_dict.get("strategy_opt", None)
        if strategy_opt is not None:
            command = "\t\techo prj_set_strategy_value '{}' >> $@".format(strategy_opt)
            self.writeln(command)