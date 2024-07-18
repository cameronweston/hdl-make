target = "microsemi"
action = "synthesis"
syn_tool = "liberosoc"

syn_family = "IGLOO2"
syn_device = "M2GL025"
syn_grade = "-1"
syn_package = "484 FBGA"

syn_top = "?.repinned_top"
syn_project = "demo"


modules = {
  "local" : [ "rtl/lib_c" ],
}

