module repro (input ia);
   wire       a;
   wire [0:31] s;

//   assign s = "hell";
  (* attr *)
  mygate inst (a);
endmodule
