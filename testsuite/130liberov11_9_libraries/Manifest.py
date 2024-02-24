target = "microsemi"
action = "synthesis"
syn_tool = "libero"

syn_tool="libero"
syn_family="ProASIC3"
syn_device="anfpga"
syn_grade="3"
syn_package="ff"

syn_top = "repinned_top"
syn_project = "demo"


modules = {
  "local" : [ "rtl/lib_c" ],
}

