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

"""Module providing support for Lattice Diamond IDE"""


from __future__ import absolute_import
from .makefilesyn import MakefileSyn
from ..sourcefiles.srcfile import EDFFile, LPFFile, VHDLFile, VerilogFile, IPXFile, LPCFile, RVLFile, RVAFile


class ToolDiamond(MakefileSyn):

    """Class providing the interface for Lattice Diamond synthesis"""

    TOOL_INFO = {
        'name': 'Diamond',
        'id': 'diamond',
        'windows_bin': 'pnmainc.exe',
        'linux_bin': 'diamondc',
        'project_ext': 'ldf'}

    STANDARD_LIBS = ['ieee', 'std', 'machxo2', 'machxo3']

    _LATTICE_SOURCE = 'prj_src {0} {{srcfile}}'
    _LATTICE_SETTINGS_DUMMY = '#prj_src {0} {{srcfile}}'
    _LATTICE_PURGE_SOURCE = 'prj_src remove -all'

    SUPPORTED_FILES = {
        EDFFile: _LATTICE_SOURCE.format('add'),
        LPFFile: _LATTICE_SETTINGS_DUMMY.format('add -exclude') + '; ' +
                 _LATTICE_SOURCE.format('enable'),
        IPXFile: _LATTICE_SOURCE.format('add'),
        LPCFile: _LATTICE_SOURCE.format('add'),
        RVLFile: _LATTICE_SOURCE.format('add'),
        RVAFile: _LATTICE_SOURCE.format('add')}

    HDL_FILES = {
        VHDLFile: _LATTICE_SOURCE.format('add'),
        VerilogFile: _LATTICE_SOURCE.format('add')}

    CLEAN_TARGETS = {'clean': ["*.sty", "*.ldf", "$(PROJECT)"],
                     'mrproper': ["*.jed"]}

    TCL_CONTROLS = {'create': 'prj_project new -name $(PROJECT)'
                              ' -impl $(PROJECT)'
                              ' -dev {0} -synthesis \"synplify\"',
                    'open': 'prj_project open $(PROJECT).ldf',
                    'save': 'prj_project save',
                    'close': 'prj_project close',
                    'project': '$(TCL_CREATE)\n'
                               'source files.tcl\n'
                               '$(TCL_SAVE)\n'
                               '$(TCL_CLOSE)',
                    'par': '$(TCL_OPEN)\n'
                           'prj_run PAR -impl $(PROJECT)\n'
                           '$(TCL_SAVE)\n'
                           '$(TCL_CLOSE)',
                    'bitstream': '$(TCL_OPEN)\n'
                                 'prj_run Export'
                                 ' -impl $(PROJECT) -task Bitgen\n'
                                 '$(TCL_SAVE)\n'
                                 '$(TCL_CLOSE)',
                    'prom': '$(TCL_OPEN)\n'
                            'prj_run Export'
                            ' -impl $(PROJECT) -task Jedecgen\n'
                            '$(TCL_SAVE)\n'
                            '$(TCL_CLOSE)',
                    'install_source': '$(PROJECT)/$(PROJECT)_$(PROJECT).jed',
                    'files': _LATTICE_PURGE_SOURCE}

    def __init__(self):
        super(ToolDiamond, self).__init__()
        self._tcl_controls.update(ToolDiamond.TCL_CONTROLS)

    def _makefile_syn_tcl(self):
        """Create a Diamond synthesis project by TCL"""
        syn_device = self.manifest_dict["syn_device"]
        syn_grade = self.manifest_dict["syn_grade"]
        syn_package = self.manifest_dict["syn_package"]
        create_tmp = self._tcl_controls["create"]
        target = syn_device + syn_grade + syn_package
        self._tcl_controls["create"] = create_tmp.format(target.upper())
        super(ToolDiamond, self)._makefile_syn_tcl()
