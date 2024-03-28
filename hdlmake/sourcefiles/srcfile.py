# -*- coding: utf-8 -*-
#
# Copyright (c) 2013, 2014 CERN
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

"""Module providing the source file class and a set of classes
representing the different possible files and file extensions"""

from __future__ import print_function
from __future__ import absolute_import
import os
import logging

from ..util import path as path_mod
from .dep_file import DepFile, File, ParamFile, ManualFile
import six


class SourceFile(DepFile):

    """This is a class acting as a base for the different
    HDL sources files, i.e. those that can be parsed"""

    def __init__(self, path, module):
        assert isinstance(path, six.string_types)
        self.library = module.library
        DepFile.__init__(self, path=path, module=module)

    def __hash__(self):
        s = self.path
        if self.library is not None:
            s += self.library
        return hash(s)

    def parse(self, graph):
        assert False, "to be implemented"


# SOURCE FILES

class VHDLFile(SourceFile):

    """This is the class providing the generic VHDL file"""

    def __init__(self, path, module):
        SourceFile.__init__(self, path=path, module=module)

    def parse(self, graph):
        from .vhdl_parser import VHDLParser
        self.parser = VHDLParser()
        self.parser.parse(self, graph)


class VerilogFile(SourceFile):

    """This is the class providing the generic Verilog file"""

    def __init__(self, path, module, include_dirs=None):
        SourceFile.__init__(self, path=path, module=module)
        self.include_dirs = include_dirs[:] if include_dirs else []
        self.include_dirs.append(path_mod.relpath(self.dirname))

    def parse(self, graph):
        from .vlog_parser import VerilogParser
        self.parser = VerilogParser()
        self.parser.parse(self, graph)


class SVFile(VerilogFile):
    """This is the class providing the generic SystemVerilog file"""
    pass


# TCL COMMAND FILE

class TCLFile(File):
    """This is the class providing the Tool Command Language file"""
    pass


# XILINX FILES

class UCFFile(ParamFile):
    """This is the class providing the User Constraint Guide file"""
    pass


class XISEFile(File):
    """This is the class providing the new Xilinx ISE project file"""
    pass


class CDCFile(ParamFile):
    """This is the class providing the Xilinx ChipScope Definition
    and Connection file"""
    pass


class XMPFile(File):
    """Xilinx Embedded Micro Processor"""
    pass


class PPRFile(File):
    """Xilinx PlanAhead Project"""
    pass


class XPRFile(File):
    """Xilinx Vivado Project"""
    pass


class XCOFile(File):
    """Xilinx Core Generator File"""
    pass


class NGCFile(ManualFile):
    """Xilinx Generated Netlist File"""
    pass


class XDCFile(ParamFile):
    """Xilinx Design Constraint File"""
    pass


class XCFFile(ParamFile):
    """Xilinx XST Constraint File"""
    pass


class COEFile(File):
    """Xilinx Coefficient File"""
    pass


class MIFFile(File):
    """Xilinx Memory Initialization File"""
    pass


class RAMFile(File):
    """Xilinx RAM  File"""
    pass


class HEXFile(SourceFile):
    """Memory initialization binary file in .hex format"""
    pass


class VHOFile(File):
    """Xilinx VHDL Template File"""
    pass


class BMMFile(File):
    """Xilinx Block Memory Map File"""
    pass


class VEOFile(File):
    """Xilinx Verilog Template File"""
    pass


class XCIFile(SourceFile):
    """Xilinx Core IP File"""

    def parse(self, graph):
        from .xci_parser import XCIParser
        self.parser = XCIParser()
        self.parser.parse(self, graph)


class BDFile(SourceFile):
    """Xilinx Block Design"""

    def parse(self, graph):
        from .bd_parser import BDParser
        self.parser = BDParser()
        self.parser.parse(self, graph)


class XCIXFile(SourceFile):
    """Xilinx Core Container IP File"""

    def parse(self, graph):
        from .xci_parser import XCIXParser
        self.parser = XCIXParser()
        self.parser.parse(self, graph)


XILINX_FILE_DICT = {
    'xise': XISEFile,
    'ise': XISEFile,
    'ngc': NGCFile,
    'ucf': UCFFile,
    'cdc': CDCFile,
    'xmp': XMPFile,
    'ppr': PPRFile,
    'xpr': XPRFile,
    'bd': BDFile,
    'xco': XCOFile,
    'xdc': XDCFile,
    'xcf': XCFFile,
    'coe': COEFile,
    'mif': MIFFile,
    'ram': RAMFile,
    'vho': VHOFile,
    'veo': VEOFile,
    'bmm': BMMFile,
    'xci': XCIFile,
    'xcix': XCIXFile}


# SYNOPSYS FILES

class SDCFile(ParamFile):
    """Synopsys Design Constraints"""
    pass


# LATTICE FILES

class LDFFile(File):
    """Lattice Diamond Project File"""
    pass


class LPFFile(File):
    """Lattice Preference/Constraint File"""
    pass

class PCFFile(File):
    """Icestorm Physical constraints File"""
    pass

class EDFFile(File):
    """EDIF Netlist Files"""
    pass

class IPXFile(File):
    """This is the class providing the Lattice Diamond IP Express Manifest file"""
    pass

class LPCFile(File):
    """This is the class providing the Lattice Diamond IP Express module parameter Customization file"""
    pass

class RVLFile(File):
    """This is the class providing the Lattice Diamond Reveal Inserter Project/Debug file"""
    pass

class RVAFile(File):
    """This is the class providing the Lattice Diamond Reveal Analyzer RVA file"""
    pass

class STYFile(File):
    """This is the class providing the Lattice Radiant Strategy file"""
    pass

#class SVFFile(File):
#    """This is the class providing the Lattice Diamond Reveal Analyzer SVF file"""
#    pass

LATTICE_FILE_DICT = {
    'ldf': LDFFile,
    'lpf': LPFFile,
    'edf': EDFFile,
    'edif': EDFFile,
    'edi': EDFFile,
    'edn': EDFFile,
    'pcf': PCFFile,
    'ipx': IPXFile,
    'lpc': LPCFile,
    'rvl': RVLFile,
    'rva': RVAFile,
    'sty': STYFile}


# MICROSEMI/ACTEL FILES

class PDCFile(ParamFile):
    """Physical Design Constraints"""
    pass

class CXFFile(SourceFile):
    """Microsemi IP core File"""

    def __init__(self, path, module, library=None):
        SourceFile.__init__(self, path=path, module=module, library=library)
        from .cxf_parser import CXFParser
        self.parser = CXFParser()

MICROSEMI_FILE_DICT = {
    'pdc': PDCFile,
    'cxf': CXFFile}


# OHR FILES

class WBGenFile(File):
    """Wishbone generator file"""
    pass


# INTEL/ALTERA FILES

class QIPFile(ManualFile):
    """This is the class providing the Altera Quartus IP file. It is
    expected that the declaration of QIP file is of type tuple, where
    user specifies in the manifest the provided top-level module of
    qip file."""
    pass


class QSYSFile(File):
    """Qsys - Altera's System Integration Tool"""
    pass


class IPFile(File):
    """Qsys/Platform Designer IP - Intel Platform Designer Tool IP configuration file"""
    pass


class DPFFile(File):
    """This is the class providing Altera Quartus Design Protocol File"""
    pass


class QSFFile(File):
    """Quartus Settings File"""
    pass


class BSFFile(File):
    """Quartus Block Symbol File"""
    pass


class BDFFile(File):
    """Quartus Block Design File"""
    pass


class TDFFile(File):
    """Quartus Text Design File"""
    pass


class GDFFile(File):
    """Quartus Graphic Design File"""
    pass


class SignalTapFile(File):
    """This is the class providing the Altera Signal Tap Language file"""
    pass


ALTERA_FILE_DICT = {
    'stp': SignalTapFile,
    'qip': QIPFile,
    'qsys': QSYSFile,
    'ip': IPFile,
    'dpf': DPFFile,
    'qsf': QSFFile,
    'bsf': BSFFile,
    'bdf': BDFFile,
    'tdf': TDFFile,
    'gdf': GDFFile}


VHDL_EXTENSIONS = (
    'vhd',
    'vhdl',
    'vho')


VERILOG_EXTENSIONS = (
    'v',
    'vh',
    'vo',
    'vm')

SV_EXTENSIONS = (
    'sv',
    'svh')


def create_source_file(path, module, include_dirs=None):
    """Function that analyzes the given arguments and returns a new HDL source
    file of the appropriated type"""
    assert path
    assert os.path.isabs(path)
    _, extension = os.path.splitext(path)
    assert extension[0] == '.'
    # Remove '.'
    extension = extension[1:]
    logging.debug("add file " + path)

    if extension in ("ngc", "qip"):
        logging.warning("file %s in %s has no explicit provided units, rewrite as '(filename, unit)'",
            path, module)
        new_file = File(path=path, module=module)
    elif extension in VHDL_EXTENSIONS:
        new_file = VHDLFile(path=path,
                            module=module)
    elif extension in VERILOG_EXTENSIONS:
        new_file = VerilogFile(path=path,
                               module=module,
                               include_dirs=include_dirs)
    elif extension in SV_EXTENSIONS:
        new_file = SVFile(path=path,
                          module=module,
                          include_dirs=include_dirs)
    elif extension == 'wb':
        new_file = WBGenFile(path=path, module=module)
    elif extension == 'tcl':
        new_file = TCLFile(path=path, module=module)
    elif extension == 'sdc':
        new_file = SDCFile(path=path, module=module)
    elif extension == 'xci':
        new_file = XCIFile(path=path, module=module)
    elif extension == 'cxf':
        new_file = CXFFile(path=path, module=module)
    elif extension in XILINX_FILE_DICT:
        new_file = XILINX_FILE_DICT[extension](path=path, module=module)
    elif extension in ALTERA_FILE_DICT:
        new_file = ALTERA_FILE_DICT[extension](path=path, module=module)
    elif extension in LATTICE_FILE_DICT:
        new_file = LATTICE_FILE_DICT[extension](path=path, module=module)
    elif extension in MICROSEMI_FILE_DICT:
        new_file = MICROSEMI_FILE_DICT[extension](path=path, module=module)
    else:
        raise Exception("Unknown extension '{}' for file {}".format(extension, path))
    return new_file

def create_source_file_with_deps(path, module, provide, depends):
    """Function that analyzes the given arguments and returns a new HDL source
    file of the appropriated type"""
    assert path
    assert os.path.isabs(path)
    _, extension = os.path.splitext(path)
    assert extension[0] == '.'
    # Remove '.'
    extension = extension[1:]
    logging.debug("add file (with deps) " + path)

    if extension in ['ngc', ]:
        return NGCFile(path, module, provide, depends)
    elif extension in ['qip', ]:
        return QIPFile(path, module, provide, depends)
    raise Exception("Unknown extension '{}' for file {} (with deps)".format(extension, path))
