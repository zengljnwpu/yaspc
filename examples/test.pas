program test;
var 
	i, j: integer;
	f: array[1..10] of integer;
function add2recursive(i: integer; var x: integer): integer;
begin
	if x = 2 then 
		add2recursive := i+2
	else 
	begin
		x := x+1;
		add2recursive := add2recursive(i, x);
	end;
end;
begin
	for i := 1 to 10 do
	begin
		j := 1;
		f[i] := add2recursive(i, j);
	end;
	writeln(j);
	i := 1;
	repeat
		writeln(f[i]);
		i := i+1;
	until i > 10;
end.
