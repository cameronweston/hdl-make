-- Copyright Philip Clarke 2020 - 2021
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
-- Source location: https://github.com/hdlved/vhdl2008_testcases
--
-- As per CERN-OHL-S v2 section 4, should hardware be produced using this source,
-- the product must visibly display the source location in its documentation,
--
-- -----------------------------------------------------------------------------
--
-- This code is probably available to purchase from the orgional author under a
-- different license if that suits your project better.
--
-- -----------------------------------------------------------------------------
-- This VHDL entity implements a basic pipeline stage with behaviour that matches:


library ieee;
   use ieee.std_logic_1164.all;
   use ieee.numeric_std.all;

library lib_a;
   use lib_a.register_types_pkg;

library lib_b;
   use lib_b.register_types_pkg;

entity merged_top is
   generic (
     g_AXI_Ax_ADDR_W : positive := 12;
     g_DAT_BW        : positive := 4  -- W channel (Data and strobe width control) -- Byte Width
                                     -- & also R channel
   );
   port (
      clk         : in std_logic;
      rst_n       : in std_logic;  -- sync reset

      aw_ready_a  : out std_logic;
      aw_valid_a  : in  std_logic;
      aw_ready_b  : out std_logic;
      aw_valid_b  : in  std_logic;
      aw_addr   : in  std_logic_vector( g_AXI_Ax_ADDR_W-1 downto 0);                 -----    TODO: THIS should be a BYTE_ADDR not WORD ADDR
      aw_prot   : in  std_logic_vector(          2 downto 0);

      -- write data port
      w_ready_a   : out std_logic;
      w_valid_a   : in  std_logic;
      w_ready_b   : out std_logic;
      w_valid_b   : in  std_logic;
      w_data      : in  std_logic_vector(g_DAT_BW*8 -1 downto 0);
      w_strb      : in  std_logic_vector(g_DAT_BW   -1 downto 0);

      -- write response port
      b_ready_a   : in  std_logic;
      b_valid_a   : out std_logic;
      b_resp_a    : out std_logic_vector(1 downto 0);

      b_ready_b   : in  std_logic;
      b_valid_b   : out std_logic;
      b_resp_b    : out std_logic_vector(1 downto 0);


      -- read address port
      ar_ready_a  : out std_logic;
      ar_valid_a  : in  std_logic;
      ar_ready_b  : out std_logic;
      ar_valid_b  : in  std_logic;
      ar_addr   : in  std_logic_vector(g_AXI_Ax_ADDR_W-1 downto 0);                  -----    TODO: THIS should be a BYTE_ADDR not WORD ADDR
      ar_prot   : in  std_logic_vector(                2 downto 0);

       -- read response port
      r_ready_a   : in  std_logic;
      r_valid_a   : out std_logic;
      r_data_a    : out std_logic_vector(g_DAT_BW*8 - 1 downto 0);
      r_resp_a    : out std_logic_vector(             1 downto 0);

      r_ready_b   : in  std_logic;
      r_valid_b   : out std_logic;
      r_data_b    : out std_logic_vector(g_DAT_BW*8 - 1 downto 0);
      r_resp_b    : out std_logic_vector(             1 downto 0);

      --------------------------------------------------------------------------
      regs_out_a          : out lib_a.register_types_pkg.t_regs_out;
      regs_out_b          : out lib_b.register_types_pkg.t_regs_out;
      regs_in_a           : in  lib_a.register_types_pkg.t_regs_in;
      regs_in_b           : in  lib_b.register_types_pkg.t_regs_in
   );
end entity merged_top;

architecture rtl of merged_top is
begin

   regs_a : entity lib_a.axi_regs_a
   generic map (
      g_AXI_Ax_ADDR_W => g_AXI_Ax_ADDR_W,
      g_DAT_BW        => g_DAT_BW
   ) port map (
      clk      => clk,
      rst_n    => rst_n,
      aw_ready => aw_ready_a,
      aw_valid => aw_valid_a,
      aw_addr  => aw_addr,
      aw_prot  => aw_prot,
      w_ready  => w_ready_a,
      w_valid  => w_valid_a,
      w_data   => w_data,
      w_strb   => w_strb,
      b_ready  => b_ready_a,
      b_valid  => b_valid_a,
      b_resp   => b_resp_a,
      ar_ready => ar_ready_a,
      ar_valid => ar_valid_a,
      ar_addr  => ar_addr,
      ar_prot  => ar_prot,
      r_ready  => r_ready_a,
      r_valid  => r_valid_a,
      r_data   => r_data_a,
      r_resp   => r_resp_a,
      regs_out => regs_out_a,
      regs_in  => regs_in_a
   );

   regs_b : entity lib_b.axi_regs_b
   generic map (
      g_AXI_Ax_ADDR_W => g_AXI_Ax_ADDR_W,
      g_DAT_BW        => g_DAT_BW
   ) port map (
      clk      => clk,
      rst_n    => rst_n,
      aw_ready => aw_ready_b,
      aw_valid => aw_valid_b,
      aw_addr  => aw_addr,
      aw_prot  => aw_prot,
      w_ready  => w_ready_b,
      w_valid  => w_valid_b,
      w_data   => w_data,
      w_strb   => w_strb,
      b_ready  => b_ready_b,
      b_valid  => b_valid_b,
      b_resp   => b_resp_b,
      ar_ready => ar_ready_b,
      ar_valid => ar_valid_b,
      ar_addr  => ar_addr,
      ar_prot  => ar_prot,
      r_ready  => r_ready_b,
      r_valid  => r_valid_b,
      r_data   => r_data_b,
      r_resp   => r_resp_b,
      regs_out => regs_out_b,
      regs_in  => regs_in_b
   );


end architecture rtl;