entity gate is
  port (i : in bit;
        o : out bit);
end gate;

architecture behav of gate is
begin
  o <= not i;
end behav;
