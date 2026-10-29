C=print
D=range
import sys as B,time as E
def I(A,B,C,n):
	for E in D(n):
		for F in D(n):
			for G in D(n):C[E*n+F]+=A[E*n+G]*B[G*n+F]
def A():
	if len(B.argv)!=2:C(f"Usage: {B.argv[0]} <size>",file=B.stderr);B.exit(1)
	A=int(B.argv[1])
	if A%8!=0:A+=8-A%8
	C(f"number of rows x cols: {A}");J=[1.]*(A*A);K=[1.]*(A*A);F=[.0]*(A*A);L=E.perf_counter();I(J,K,F,A);M=E.perf_counter();N=M-L;O=['bad','ok'];G=1
	for P in D(A):
		H=False
		for Q in D(A):
			if F[P*A+Q]!=float(A):G=0;H=True;break
		if H:break
	C(f"multiply values are {O[G]}\ntime: {N:.3f} seconds")
if __name__=='__main__':A()