program dsq;
var n:longint;
	f:boolean;

function prime(num: integer): boolean;
var i:longint;
	g:boolean;
begin
for i:=2 to num do 
	if num mod i = 0 then g:=true;
prime:=g;
end;

begin
	n:=123;
	f:=false;
	f:=prime(n);
end.