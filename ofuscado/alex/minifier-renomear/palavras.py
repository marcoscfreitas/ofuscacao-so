H=range
E=print
import sys as C,time as G
A=8
def B():
	if len(C.argv)!=2:E(f"Usage: {C.argv[0]} <size>",file=C.stderr);C.exit(1)
	B=int(C.argv[1])
	if B%A!=0:B+=A-B%A
	E(f"number of words: {B}");J=[f"word{B%A}"for B in H(B)];F={};K=G.perf_counter()
	for D in J:F[D]=F.get(D,0)+1
	L=G.perf_counter();M=L-K;N=['bad','ok'];I=1;O=B//A
	for P in H(A):
		D=f"word{P}"
		if F.get(D,0)!=O:I=0;break
	E(f"word counts are {N[I]}\ntime: {M:.3f} seconds")
if __name__=='__main__':B()