files = [
    "merged_top.vhd",
    "repinned_top.vhd",
]

library = "lib_c"

modules = { "local" : ["../lib_a",
                       "../lib_b",
                      ]
}

# if we are simulating this will be handy... 
vcom_opt = "-93 +check_synthesis -mixedsvh -check_synthesis"