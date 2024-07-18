entity gate6 is
  port (i : in bit;
        o : out bit);
end gate6;

architecture behav of gate6 is
begin
  inst: entity gatelib.gate
    port map (i, o);
end behav;
