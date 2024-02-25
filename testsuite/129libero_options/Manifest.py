action = "synthesis"

syn_tool="libero"
syn_family="ProASIC3"
syn_device="anfpga"
syn_grade="3"
syn_package="ff"
syn_project="gate"
syn_io_deft_std="LVCMOS18"
project_opt="-adv_options {IO_DEFT_STD:LVCMOS18} -adv_options {syn_rad_exp:15}"

top_module = "gate"

files = [ "../files/gate.vhdl", "syn.sdc", "comp.pdc" ]
