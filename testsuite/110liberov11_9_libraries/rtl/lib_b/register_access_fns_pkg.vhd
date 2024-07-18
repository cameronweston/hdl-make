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

--  Register_access_functions package...
--    This is intended to show how a byte-address -> record based IF can work.
--    a file like this can be machine-generated and is very human readable!
--    this file is also bus protocol agnostic.
--       e.g. the same source file can be used for different bus protocols
--    This byte -> record approach also allows for genericisation of
--                width
--                if byte-enables are used on a per instance basis
--                pipelining

library ieee;
   use ieee.std_logic_1164.all;
   use ieee.numeric_std.all;

-- library work;
   use work.register_types_pkg.all;

package register_access_fns_pkg is

   procedure p_write_byte (
                      byte_addr   : in    natural;
                      wr_prot     : in    std_logic_vector(2 downto 0);
                      wr_byte     : in    std_logic_vector(7 downto 0);
               signal regs_out    : inout t_regs_out;
                      bad_wr_addr : out   boolean;
                      wr_prot_err : out   boolean
             );

   procedure p_do_wc ( signal regs_out : inout t_regs_out);

   procedure p_do_wr_reset ( signal regs_out : inout t_regs_out);


   procedure p_read_byte (
                byte_addr   : in  natural;
                rd_prot     : in  std_logic_vector(2 downto 0);
                regs_out    : in  t_regs_out;
                regs_in     : in  t_regs_in;
                bad_rd_addr : out boolean;
                rd_prot_err : out boolean;
                rd_byte     : out std_logic_vector(7 downto 0)
             );

   -- OK we could have a proc for RC bits

end package;

package body register_access_fns_pkg is

   procedure p_write_byte (
                       byte_addr   : in    natural;
                       wr_prot     : in    std_logic_vector(2 downto 0);
                       wr_byte     : in    std_logic_Vector(7 downto 0);
                signal regs_out    : inout t_regs_out;
                       bad_wr_addr : out   boolean;
                       wr_prot_err : out   boolean
             ) is
   begin
      bad_wr_addr := false;
      wr_prot_err := false;
      case (byte_addr) is
         when 0      => regs_out.scratchpad( 7 downto  0) <= wr_byte;
         when 1      => regs_out.scratchpad(15 downto  8) <= wr_byte;
         when 2      => regs_out.scratchpad(23 downto 16) <= wr_byte;
         when 3      => regs_out.scratchpad(31 downto 24) <= wr_byte;

         when 4      => regs_out.b_2_a <= wr_byte(regs_out.b_2_a'range);

         when 8      => regs_out.wc_examples <= wr_byte(1 downto 0);

         when 12     => regs_out.leds <= wr_byte(regs_out.leds'range);

         when 31     => wr_prot_err := true;

         when others => bad_wr_addr := true;
      end case;
      regs_out.last_aw_prot <= wr_prot;
   end procedure;


   procedure p_do_wc ( signal regs_out : inout t_regs_out)
   is
   begin
      regs_out.wc_examples <= (others => '0');
      regs_out.leds(0)     <= '0';
   end procedure;

   procedure p_do_wr_reset ( signal regs_out : inout t_regs_out)
   is
   begin
      regs_out.b_2_a       <= (others => '0');
      regs_out.wc_examples <= (others => '0');
      regs_out.leds        <= (others => '1');

   end procedure;


   procedure p_read_byte (
                   byte_addr   : in  natural;
                   rd_prot     : in  std_logic_vector(2 downto 0);
                   regs_out    : in  t_regs_out;
                   regs_in     : in  t_regs_in;
                   bad_rd_addr : out boolean;
                   rd_prot_err : out boolean;
                   rd_byte     : out std_logic_vector(7 downto 0)
                ) is
   begin
      rd_byte     := (others => '0');
      bad_rd_addr := false;
      rd_prot_err := false;
      case (byte_addr) is
         when 0      => rd_byte := regs_out.scratchpad( 7 downto  0);
         when 1      => rd_byte := regs_out.scratchpad(15 downto  8);
         when 2      => rd_byte := regs_out.scratchpad(23 downto 16);
         when 3      => rd_byte := regs_out.scratchpad(31 downto 24);

         when 4      => rd_byte(regs_in.a_2_b'range) := regs_in.a_2_b;

         when 12     => rd_byte(regs_out.leds'range) := regs_out.leds;

         when 16     => rd_byte(2 downto 0) := regs_in.switches;

         when 20     => rd_prot_err := true;
         when 21     => rd_byte(2 downto 0) := regs_out.last_aw_prot;
         when others => bad_rd_addr := true;
      end case;
   end procedure;



end package body register_access_fns_pkg;