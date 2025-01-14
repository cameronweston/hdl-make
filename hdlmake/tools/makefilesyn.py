"""Module providing the synthesis functionality for writing Makefiles"""

from __future__ import absolute_import
import os, sys
import logging

from .makefile import ToolMakefile
from ..util import shell


def _check_synthesis_manifest(top_manifest):
    """Check the manifest contains all the keys for a synthesis project"""
    for v in ["syn_top", "syn_device", "syn_grade", "syn_package"]:
        if v not in top_manifest.manifest_dict:
            raise Exception(
                "'{}' variable must be set in the top manifest.".format(v))
    # Tools with multithread support
    if "syn_jobs" in top_manifest.manifest_dict:
        for v in ["vivado"]:
            if v != top_manifest.manifest_dict["syn_tool"]:
                logging.warning("'syn_jobs' is ignored for '{}' tool".format(top_manifest.manifest_dict["syn_tool"]))


class MakefileSyn(ToolMakefile):

    """Class that provides the synthesis Makefile writing methods and status"""
    ACTION_SHORTNAME = "syn"

    """Makefile template to build and execute a command.
    Arguments:
    {0}: name of the stage (project, bitstream, ...)
    {1}: previous stage (for dependency)
    {2}: name of the stage, in upper case
    {3}: commands to create the tcl script
    {4}: touch command"""
    MAKEFILE_SYN_BUILD_CMD="""\
{0}.tcl:
{3}

{0}: {1} {0}.tcl{deps}
\t\t$(SYN_PRE_{2}_CMD)
\t\t$(TCL_INTERPRETER) $@.tcl
\t\t$(SYN_POST_{2}_CMD)
\t\t{4} $@
"""

    def __init__(self):
        super(MakefileSyn, self).__init__()
        self._tcl_controls = {}

    def write_makefile(self, top_manifest, fileset, filename=None):
        """Generate a Makefile for the specific synthesis tool"""
        _check_synthesis_manifest(top_manifest)
        self.makefile_setup(top_manifest, fileset, filename=filename)
        self.makefile_check_tool('syn_path')
        self.makefile_includes()
        self._makefile_syn_top()
        self._makefile_syn_tcl()
        self._makefile_syn_local()
        self._makefile_syn_files()
        self._makefile_syn_command()
        self._makefile_syn_build()
        self._makefile_syn_clean()
        self._makefile_syn_phony()
        self.makefile_open_write_close()
        logging.info(self.TOOL_INFO['name'] + " synthesis makefile generated.")

    def _makefile_syn_top(self):
        """Create the top part of the synthesis Makefile"""
        top_parameter = """\
TOP_LIBRARY := {top_library}
TOP_MODULE := {top_module}
PROJECT := {project_name}
PROJECT_FILE := $(PROJECT).{project_ext}
TOOL_PATH := {tool_path}
TCL_INTERPRETER := {tcl_interpreter}
ifneq ($(strip $(TOOL_PATH)),)
TCL_INTERPRETER := $(TOOL_PATH)/$(TCL_INTERPRETER)
endif

SYN_FAMILY := {syn_family}
SYN_DEVICE := {syn_device}
SYN_PACKAGE := {syn_package}
SYN_GRADE := {syn_grade}
"""
        self.writeln(top_parameter.format(
            tcl_interpreter=self.get_tool_bin(),
            project_name=os.path.splitext(
                self.manifest_dict["syn_project"])[0],
            project_ext=self.TOOL_INFO["project_ext"],
            syn_family=self.manifest_dict.get("syn_family", ''),
            syn_device=self.manifest_dict["syn_device"],
            syn_package=self.manifest_dict["syn_package"],
            syn_grade=self.manifest_dict["syn_grade"],
            tool_path=self.manifest_dict["syn_path"],
            top_library=self.get_top_library(),
            top_module=self.get_top_module()))

    def _makefile_syn_prj_tcl_cmd(self):
        """Create the Makefile variables for the TCL project commands."""
        for command in ["create", "open", "save", "close"]:
            if command in self._tcl_controls:
                self.writeln('TCL_{} := {}'.format(
                    command.upper(), self._tcl_controls[command]))

    def _makefile_syn_override_prj_tcl_create(self):
        """Override the TCL create project command by the open one if
        the project already exists"""
        self.writeln("""\
ifneq ($(wildcard $(PROJECT_FILE)),)
TCL_CREATE := $(TCL_OPEN)
endif""")
        self.writeln()

    def _makefile_syn_tcl(self):
        """Create the Makefile TCL dictionary for the selected tool"""
        self._makefile_syn_prj_tcl_cmd()
        self._makefile_syn_override_prj_tcl_create()


    def _makefile_syn_files_predefinelibs(self):
        """Stub to allow a child class to create libraries before adding files to the files.tcl file"""


    def _makefile_syn_files_map_files_to_lib(self):
        """Stub to allow a child class to map specific files to specific libraries when it has to be a separate command"""


    def _makefile_syn_files(self):
        """Write the files TCL section of the Makefile"""
        fileset_dict = {}

        self.writeln('files.tcl:')

        # this function will add the ligrary creation commands, and if there are none
        # it will change self.HDLFILES so that no library commands are used!
        self._makefile_syn_files_predefinelibs()        
        
        fileset_dict.update(self.HDL_FILES)
        fileset_dict.update(self.SUPPORTED_FILES)
        # Extra commands before source files.
        if "files" in self._tcl_controls:
            for command in self._tcl_controls["files"].split('\n'):
                self.writeln('\t\t@echo {0} >> $@'.format(command))

        # Add each source file
        self._makefile_syn_files_cmd(fileset_dict)

        self._makefile_syn_files_map_files_to_lib()
        self.writeln()

    def _makefile_syn_local(self):
        """Generic method to write the synthesis Makefile local target"""
        self.writeln("#target for performing local synthesis\n"
                     "all: bitstream\n")

    def _makefile_syn_build(self):
        """Generate the synthesis Makefile targets for handling design build"""
        stage_previous = "files.tcl"
        stage_list = ["project", "synthesize", "translate",
                      "map", "par", "bitstream", "prom"]
        for stage in stage_list:
            if stage in self._tcl_controls:
                echo_command = '\t\techo {0} >> $@'
                tcl_command = []
                for command in self._tcl_controls[stage].split('\n'):
                    tcl_command.append(echo_command.format(command))
                command_string = "\n".join(tcl_command)
                deps = " " + " ".join(shell.makefile_path(f) for f in self._all_sources) if stage == "synthesize" else ""
                self.writeln(self.MAKEFILE_SYN_BUILD_CMD.format(
                    stage, stage_previous, stage.upper(),
                    command_string, shell.touch_command(),
                    deps=deps))
                stage_previous = stage

    def _makefile_syn_command(self):
        """Create the Makefile targets for user defined commands"""
        stage_list = ["project", "synthesize", "translate",
                      "map", "par", "bitstream", "prom"]
        for stage in stage_list:
            if stage in self._tcl_controls:
                self.writeln("""\
SYN_PRE_{0}_CMD := {1}
SYN_POST_{0}_CMD := {2}
""".format(stage.upper(),
           self.manifest_dict.get("syn_pre_" + stage + "_cmd", ''),
           self.manifest_dict.get("syn_post_" + stage + "_cmd", '')))

    def _makefile_syn_clean(self):
        """Print the Makefile clean target for synthesis"""
        self.makefile_clean()
        _stage_clean_targets=""
        _stage_tcl_clean_targets=""
        stage_list = ["project", "synthesize", "translate",
                      "map", "par", "bitstream", "prom"]
        for stage in stage_list:
            if stage in self._tcl_controls:
                _stage_clean_targets += " %s" % (stage)
                _stage_tcl_clean_targets += " %s.tcl" % (stage)
        _stage_tcl_clean_targets+=" files.tcl"
        self.writeln("\t\t" + shell.del_command() + _stage_clean_targets)
        self.writeln("\t\t" + shell.del_command() + _stage_tcl_clean_targets)
        self.writeln()
        self.makefile_mrproper()

    def _makefile_syn_phony(self):
        """Print synthesis PHONY target list to the Makefile"""
        self.writeln(
            ".PHONY: mrproper clean all")

    def get_all_libs(self):
        """Return a sorted list of all the libraries name"""
        # BUG: need to filter this down to VHDL, VERILOG, SystemVERILOG
        fileset_dict = {}
        sources_with_libs_list = []
        fileset_dict.update(self.HDL_FILES)
        for filetype in fileset_dict:
          for specific_file in self.fileset:
            if isinstance(specific_file, filetype):
              sources_with_libs_list.append(specific_file)	
        return sorted(set(f.library for f in sources_with_libs_list))
