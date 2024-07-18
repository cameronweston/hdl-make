action = "simulation"

sim_tool="modelsim"

library = "gatetop"

top_module = ".gate6"

modules = {
    'local': [
        'gatelib',
    ],
}

files = [ "../files/gate6.vhdl" ]
