-- Copyright Philip Clarke 2021
--
-- ---------------------------------------------------------------------
-- This source describes Open Hardware and is licensed under the CERN-OHL-S v2.
-- You may redistribute and modify this source and make products using it
-- under the terms of the CERN-OHL-S v2 (https://ohwr.org/cern_ohl_s_v2.txt).
--
-- This source is distributed WITHOUT ANY EXPRESS OR IMPLIED
-- WARRANTY, INCLUDING OF MERCHANTABILITY, SATISFACTORY
-- QUALITY AND FITNESS FOR A PARTICULAR PURPOSE. Please see
-- the CERN-OHL-S v2 for applicable conditions.
--
-- Source location: https://github.com/hdlved/regs_and_lib_hdlmake_experiment
--
-- As per CERN-OHL-S v2 section 4, should hardware be produced using this source,
-- the product must visibly display the source location in its documentation.
--
-- -----------------------------------------------------------------------------
--
-- This code is probably available to purchase from the orgional author under a
-- different license if that suits your project better.
--
-- -----------------------------------------------------------------------------
-- This is code designed to test hdlmake and FPGA tools for VHDL library support:

--  Registers package...
--    this is intended as an example "protoclol agnostic" way to get data into and out of a VHDL 
--    register interface module. A simple VHDL record is used to pass the data out of a particular
--    CSR instance and privide the record to whatever modules need it. This is not as flexible as 
--    a SystemVerilog modport; but allows for a self-contained definition of feilds and locations 
--    of a feilds in a address space
--   This also simplifies having a specific register firl for AXI AVALON_MM or WB for example... 

--   NOTE tie differences between this file and that in lib_a

library ieee;
   use ieee.std_logic_1164.all;
   use ieee.numeric_std.all;


package register_types_pkg is

-- -----------------------------------------------------------------------------
--  Control record and "defined values"  signals controlled by a register module
-- -----------------------------------------------------------------------------
   type t_regs_out is record
       scratchpad        : std_logic_vector(31 downto 0);
       b_2_a             : std_logic_vector(7 downto 0);
       wc_examples       : std_logic_vector(1 downto 0);
       leds              : std_logic_vector(2 downto 0);
       last_aw_prot      : std_logic_vector(2 downto 0);
   end record t_regs_out;


   type t_regs_in is record
       a_2_b         : std_logic_vector(3 downto 0);
       switches      : std_logic_vector(2 downto 0);
   end record t_regs_in;


end package;

package body register_types_pkg is




end package body register_types_pkg;