#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 - 2019 CERN
# Author: Pawel Szostek (pawel.szostek@cern.ch)
#		  Adopted to LiberoSoC v12.x by Severin Haas (severin.haas@cern.ch)
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

"""Module providing support for Microsemi Libero SoC 12.x synthesis"""


from __future__ import absolute_import
from .makefilesyn import MakefileSyn
from ..sourcefiles.srcfile import VHDLFile, VerilogFile, SDCFile, PDCFile, CXFFile, SourceFile
from ..util import shell


import logging


class ToolLiberoSoC(MakefileSyn):

    """Class providing the interface for Microsemi Libero SoC 12.x synthesis"""

    TOOL_INFO = {
        'name': 'LiberoSoC',
        'id': 'liberosoc',
        'windows_bin': 'libero.exe SCRIPT:',
        'linux_bin': 'libero SCRIPT:',
        'project_ext': 'prjx'}

    STANDARD_LIBS = ['ieee', 'std']

    _LIBERO_SOURCE = 'create_links {0} {{srcfile}}'
    _LIBERO_LIB = 'add_file_to_library -library {{library}} -file {{srcfile}}'

    SUPPORTED_FILES = {
        SDCFile: _LIBERO_SOURCE.format('-sdc'),
        PDCFile: _LIBERO_SOURCE.format('-io_pdc')}

    HDL_FILES = {
        VHDLFile: _LIBERO_SOURCE.format('-hdl_source'),
        VerilogFile: _LIBERO_SOURCE.format('-hdl_source'),
        CXFFile: ''}


    HDL_LIBRARIES = {
           VHDLFile: _LIBERO_LIB.format(),
           VerilogFile: _LIBERO_LIB.format()
                    }


    CLEAN_TARGETS = {'clean': ["$(PROJECT)", "*.log"],
                     'mrproper': ["*.pdb", "*.stp"]}


    TCL_CONTROLS = {
        'create': 'new_project -location {{./{0}}} '
                  '-name {{{0}}} -hdl {{{1}}} '
                  '-family {{{2}}} -die {{{3}}} '
                  '-package {{{4}}} -speed {{{5}}}',
        'open': 'open_project -file {$(PROJECT)/$(PROJECT_FILE)}',
        'save': 'save_project',
        'close': 'close_project',
        'project': '$(TCL_CREATE)\n'
                   'source files.tcl\n'
                   'refresh\n'
                   '{0}\n'
                   '$(TCL_SAVE)\n'
                   '$(TCL_CLOSE)',
        'bitstream': ' Device not supported, so no bitstream for now!',
        'install_source': '$(PROJECT)/designer/impl1/$(SYN_TOP).pdb'}

    # Override the build command, because no space is expected between TCL_INTERPRETER and the tcl file
    MAKEFILE_SYN_BUILD_CMD="""\
{0}.tcl:
{3}

{0}: {1} {0}.tcl
\t$(SYN_PRE_{2}_CMD)
\t$(TCL_INTERPRETER)$@.tcl LOGFILE:{0}_output.log
\t$(SYN_POST_{2}_CMD)
\t{4} $@
"""


    _BITSTREAM_POLARFIRESOC =  "$(TCL_OPEN)\n"\
                             + "run_tool -name {GENERATEPROGRAMMINGDATA}\n" \
                             + "file mkdir ./$(PROJECT)/bitstream\n" \
                             + "export_bitstream_file "\
                             + "-file_name {$(PROJECT)} "\
                             + "-export_dir {$(PROJECT)/bitstream} "\
                             + "-format {STP} -trusted_facility_file 1 "\
                             + "-trusted_facility_file_components {FABRIC} \n"\
                             + "$(TCL_SAVE)\n"\
                             + "$(TCL_CLOSE)"


    _BITSTREAM_IGLOO2 =        "$(TCL_OPEN)\n"\
                             + "run_tool -name {GENERATEPROGRAMMINGDATA}\n" \
                             + "file mkdir ./$(PROJECT)/bitstream\n" \
                             + "export_bitstream_file "\
                             + "-file_name {$(PROJECT)} "\
                             + "-export_dir {$(PROJECT)/bitstream} "\
                             + "-format {STP} -trusted_facility_file 1 "\
                             + "-trusted_facility_file_components {FABRIC} "\
                             + "-serialization_stapl_type {SINGLE} "\
                             + "-serialization_target_solution {FLASHPRO_3_4_5}\n"\
                             + "$(TCL_SAVE)\n"\
                             + "$(TCL_CLOSE)"

    def __init__(self):
        super(ToolLiberoSoC, self).__init__()
        self._tcl_controls.update(ToolLiberoSoC.TCL_CONTROLS)


    def _makefile_syn_files_predefinelibs(self):
        """create libraries before adding files to the files.tcl file"""
        libraries = self.get_all_libs()
        if len(libraries) > 1:
          for libname in  libraries:
            self.writeln('\t\t@echo add_library -library ' + libname + ' >> $@')

        # PROBABLY NAUGHTY:   as at this point we know what the device type is; let's also adjust the
        # TCL_CONTROLS[bitstream] so it is device appropriate
        # shouldl this really be done in : _makefile_syn_top??
        syn_family = self.manifest_dict.get("syn_family", '')
        #logging.info(self.TOOL_INFO['name'] + " _makefile_syn_files_predefinelibs got family_name as:" + syn_family)
        if syn_family == "PolarFireSoC":
           self._tcl_controls['bitstream'] = self._BITSTREAM_POLARFIRESOC
          #logging.info(self.TOOL_INFO['name'] + " set GENERATEPROGRAMMINGDATA for SOC.")
        elif syn_family == "IGLOO2" or syn_family == 'SmartFusion2' or syn_family == "RTG4":
           self._tcl_controls['bitstream'] = self._BITSTREAM_IGLOO2
           #logging.info(self.TOOL_INFO['name'] + " set GENERATEPROGRAMMINGDATA for FPGA fabric.")
        else:
           logging.info(self.TOOL_INFO['name'] + ":TODO:  Somebody needs to add device support for this family, PolarFireSoC and IGLOO2 are supported. Can you do it?")

    def _makefile_syn_files_map_files_to_lib(self):
        """map specific files to specific libraries when it has to be a separate command"""
        fileset_dict = {}
        fileset_dict.update(self.HDL_LIBRARIES)

        libraries = self.get_all_libs()
        if len(libraries) > 1:
          for srcfile in self.fileset.sort():
            command = fileset_dict.get(type(srcfile))
            # Put the file in files.tcl only if it is supported.
            #logging.info(self.TOOL_INFO['name'] + " looping")

            if command is not None:
                # Libraries are defined only for hdl files.
                if isinstance(srcfile, SourceFile):
                    library = srcfile.library
                else:
                    library = None

                command = command.format(srcfile=shell.tclpath(srcfile.rel_path()),
                                         library=library)
                command = "\t\techo '{}' >> $@".format(command)
                self.writeln(command)

    def _makefile_syn_tcl(self):
        """Create a Libero synthesis project by TCL"""
        syn_project = self.manifest_dict["syn_project"]
        syn_device = self.manifest_dict["syn_device"]
        syn_family = self.manifest_dict["syn_family"]
        syn_grade = self.manifest_dict["syn_grade"]
        syn_package = self.manifest_dict["syn_package"]
        syn_lang = self.manifest_dict.get("language", "VHDL")
        syn_extra_tcl_files = self.manifest_dict.get('syn_project_extra_files', [])
        project_opt = self.manifest_dict.get('project_opt', None)

        # Expand create command
        create_tmp = self._tcl_controls["create"]
        create_tmp = create_tmp.format(syn_project,
                                       syn_lang.upper(),
                                       syn_family,
                                       syn_device.upper(),
                                       syn_package.upper(),
                                       syn_grade)
        if project_opt is not None:
            create_tmp += ' ' + project_opt
        self._tcl_controls["create"] = create_tmp

        # Expand project command
        project_tmp = self._tcl_controls["project"]
        synthesis_constraints   = []
        compilation_constraints = []
        timing_constraints = []
        ret = []

        library_for_top_module = str(self.get_library_for_top_module())

        libraries = self.get_all_libs()
        if len(libraries) > 1:
           line = 'set_root -module {$(TOP_MODULE)::' + library_for_top_module + '}'
        else:
           line = 'set_root -module {$(TOP_MODULE)}'
        ret.append(line)

        # First stage: linking files
        for file_aux in self.fileset.sort():
            if isinstance(file_aux, SDCFile):
                synthesis_constraints.append(file_aux)
                compilation_constraints.append(file_aux)
                timing_constraints.append(file_aux)
            elif isinstance(file_aux, PDCFile):
                compilation_constraints.append(file_aux)
        # Second stage: Organizing / activating synthesis constraints (the top
        # module needs to be present!)
        if synthesis_constraints:
            line = 'organize_tool_files -tool {SYNTHESIZE} '
            for file_aux in synthesis_constraints:
                line = line + '-file {' + file_aux.rel_path() + '} '
            line = line + \
                '-module {$(TOP_MODULE)::' + library_for_top_module + '} -input_type {constraint} '
            ret.append(line)
        # Third stage: Organizing / activating compilation constraints (the top
        # module needs to be present!)
        if compilation_constraints:
            line = 'organize_tool_files -tool {PLACEROUTE} '
            for file_aux in compilation_constraints:
                line = line + '-file {' + file_aux.rel_path() + '} '
            line = line + \
                '-module {$(TOP_MODULE)::' + library_for_top_module + '} -input_type {constraint} '
            ret.append(line)

        # is this device dependant?
        if timing_constraints:
            line = 'organize_tool_files -tool {VERIFYTIMING} '
            for file_aux in timing_constraints:
                line = line + '-file {' + file_aux.rel_path() + '} '
            line = line + \
                '-module {$(TOP_MODULE)::' + library_for_top_module + '} -input_type {constraint} '
            ret.append(line)

        # Source extra tcl files
        for f in syn_extra_tcl_files:
            ret.append('source {}'.format(f))

        self._tcl_controls['project'] = project_tmp.format('\n'.join(ret))
        super(ToolLiberoSoC, self)._makefile_syn_tcl()
