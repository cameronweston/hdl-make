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

   use work.register_types_pkg.all;
   use work.register_access_fns_pkg.all;

entity axi_regs_b is
   generic (
     g_AXI_Ax_ADDR_W : positive;
     g_DAT_BW        : positive   -- W channel (Data and strobe width control) -- Byte Width
                                  -- & also R channel
   );
   port (
      clk         : in std_logic;
      rst_n       : in std_logic;  -- sync reset

      aw_ready  : out std_logic;
      aw_valid  : in  std_logic;
      aw_addr   : in  std_logic_vector( g_AXI_Ax_ADDR_W-1 downto 0);                 -----    TODO: THIS should be a BYTE_ADDR not WORD ADDR
      aw_prot   : in  std_logic_vector(                 2 downto 0);

      -- write data port
      w_ready   : out std_logic;
      w_valid   : in  std_logic;
      w_data    : in  std_logic_vector(g_DAT_BW*8 -1 downto 0);
      w_strb    : in  std_logic_vector(g_DAT_BW   -1 downto 0);

      -- write response port
      b_ready   : in  std_logic;
      b_valid   : out std_logic;
      b_resp    : out std_logic_vector(1 downto 0);


      -- read address port
      ar_ready  : out std_logic;
      ar_valid  : in  std_logic;
      ar_addr   : in  std_logic_vector(g_AXI_Ax_ADDR_W-1 downto 0);                  -----    TODO: THIS should be a BYTE_ADDR not WORD ADDR
      ar_prot   : in  std_logic_vector(                2 downto 0);

       -- read response port
      r_ready   : in  std_logic;
      r_valid   : out std_logic;
      r_data    : out std_logic_vector(g_DAT_BW*8 - 1 downto 0);
      r_resp    : out std_logic_vector(             1 downto 0);

      --------------------------------------------------------------------------
      regs_out          : out t_regs_out;
      regs_in           : in  t_regs_in
   );
end entity axi_regs_b;

architecture rtl of axi_regs_b is

   signal do_write_this_cycle : std_logic;

   signal do_read_this_cycle : std_logic;


   signal wr_regs_int : t_regs_out;

   signal int_r_valid : std_logic;
   signal b_valid_int : std_logic;
begin

  regs_out <= wr_regs_int;


  do_read_this_cycle <= r_ready and ar_valid and not int_r_valid;


  ar_ready <= do_read_this_cycle;
  r_valid  <= int_r_valid;

  proc_read : process (clk)
    variable v_bad_addr : boolean;
    variable v_prot_err : boolean;
    variable v_rd_val   : std_logic_vector(r_data'range);
    variable v_good_addr : boolean;
  begin
     if rising_edge(clk) then
        if int_r_valid = '1' and r_ready = '1' then
          int_r_valid <= '0';
        end if;
        if do_read_this_cycle = '1' then
           r_resp       <= "00";  -- == OKAY
           v_good_addr  := false;
           for byteno in 0 to g_DAT_BW-1 loop
              p_read_byte( byte_addr   => to_integer(unsigned(ar_addr) + byteno),
                           rd_prot     => ar_prot,
                           regs_out    => wr_regs_int,
                           regs_in     => regs_in,
                           bad_rd_addr => v_bad_addr,
                           rd_prot_err => v_prot_err,
                           rd_byte     => v_rd_val((byteno + 1) * 8 -1 downto byteno * 8)
                          );
              if v_prot_err then
                 r_resp       <= "11";  -- == EXOKAY (OK ,I am not doing exclusice accesses and this is a bodge to not strip out the signal..
              end if;
              if not v_bad_addr then
                 v_good_addr := true;
              end if;
           end loop;

           if not v_good_addr then
              r_resp       <= "10";   -- ==  slv_err
           end if;

           r_data       <= v_rd_val;
           int_r_valid  <= '1';
        end if;
        if rst_n = '0' then
           int_r_valid  <= '0';
        end if;
     end if;
  end process;


  do_write_this_cycle <= aw_valid and w_valid and b_ready and not b_valid_int;

  w_ready  <= do_write_this_cycle;
  aw_ready <= do_write_this_cycle;
  b_valid  <= b_valid_int;


  proc_write : process (clk)
    variable v_bad_addr      : boolean;
    variable v_prot_err      : boolean;
    variable v_good_addr     : boolean;
    variable v_prot_err_word : boolean;
  begin
    if rising_edge(clk) then
       p_do_wc(wr_regs_int);
       if b_valid_int = '1' and b_ready = '1' then
          b_valid_int <= '0';
       end if;
       if do_write_this_cycle = '1' then
          b_resp      <= "00";
          b_valid_int <= '1';
          v_good_addr := false;
          v_prot_err_word  := false;
          for byteno in 0 to g_DAT_BW-1 loop
             if w_strb(byteno) = '1' then
                p_write_byte(
                             byte_addr   => to_integer(unsigned(aw_addr) + byteno),  -- assumes aw_Addr is always word aligned...
                             wr_prot     => aw_prot,
                             wr_byte     => w_data((byteno*8) + 7 downto (byteno*8)),
                             regs_out    => wr_regs_int,
                             bad_wr_addr => v_bad_addr,
                             wr_prot_err => v_prot_err
                            );
                if not v_bad_addr then
                   v_good_addr := true;
                end if;
                if v_prot_err then
                   v_prot_err_word := true;
                end if;
             end if;
          end loop;
          if not v_good_addr then
             b_resp      <= "10";  -- SLVERR
          end if;

          if v_prot_err_word then
            b_resp      <= "11";   -- deliberatley the WRONG_CODE this is DECERR not SLVERR
          end if;
       end if;
       if rst_n = '0' then
          p_do_wr_reset(wr_regs_int);
          b_valid_int <= '0';
       end if;
    end if;
  end process;


end architecture rtl;