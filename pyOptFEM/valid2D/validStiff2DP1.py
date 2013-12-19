import numpy,sympy,time
from ..FEM2D import *
from .common import *

VersionList = [ 'base','OptV1','OptV2']
valid_defaults ={ 'versions':VersionList }

class TestStiff:
  def __init__(self, cu,cv):
    x, y = sympy.symbols('x y')
    self.cu=cu
    self.cv=cv
    self.u=sympy.Lambda((x,y),cu)
    self.v=sympy.Lambda((x,y),cv)
    self.fu=eval("lambda x,y: "+cu)
    self.fv=eval("lambda x,y: "+cv)
    if self.u.is_polynomial(x,y):
      D=sympy.polys.Poly(cu,x,y).as_dict()
      self.du=max(numpy.sum(list(D.keys()),axis=1))
    else:
      self.du=-1
    if self.v.is_polynomial(x,y):
      D=sympy.polys.Poly(cv,x,y).as_dict()
      self.dv=max(numpy.sum(list(D.keys()),axis=1))
    else:
      self.dv=-1
    self.I=sympy.integrate(sympy.integrate(sympy.diff(self.u(x,y),x)*sympy.diff(self.v(x,y),x)+
                                           sympy.diff(self.u(x,y),y)*sympy.diff(self.v(x,y),y),(x,0,1)),(y,0,1))
    
def validStiff2DP1(**kwargs):
  """ validation of stiffness matrix assembling functions 
  """
  Plot=kwargs.get('plot',True)
  Verbose=kwargs.get('verbose',True)
  print('**********************************************')
  print('*     2D Stiff Assembling P1 validations     *')
  print('**********************************************')    

  Th=SquareMesh(10)

  LF=[['x+2*y','3*x+y+1'],
      ['x**2+2*y*x+y','3*x*y+y**2+1'],
      ['x**3+2*y**2*x+y**2+x','2*x*y+y**3+x*y']]
  if Verbose:     
    print('-----------------------------------------')
    print('  Test 1: Matrices errors and CPU times  ')
    print('-----------------------------------------')

  T=np.zeros(3)
  E=np.zeros(2)
  tstart=time.time()
  Mbase=StiffAssembling2DP1base(Th.nq,Th.nme,Th.q,Th.me,Th.areas)
  T[0]=time.time()-tstart
  if Verbose: print("    Matrix size           : (%d,%d)" % Mbase.shape)
  tstart=time.time()
  MOptV1=StiffAssembling2DP1OptV1(Th.nq,Th.nme,Th.q,Th.me,Th.areas)
  T[1]=time.time()-tstart
  E[0]=NormInf(Mbase-MOptV1)
  if Verbose: print("    Error base vs OptV1   : %e" % E[0])
  q=Th.q;me=Th.me
  tstart=time.time()
  MOptV2=StiffAssembling2DP1OptV2(Th.nq,Th.nme,q,me,Th.areas)
  T[2]=time.time()-tstart
  E[1]=NormInf(Mbase-MOptV2)
  if Verbose: 
    print("    Error base vs OptV2   : %e" % E[1])
    print("    CPU times base (ref)  : %3.4f (s)" % T[0])
    print("    CPU times OptV1       : %3.4f (s) - Speed Up X%3.3f" % (T[1],T[0]/T[1]))
    print("    CPU times OptV2       : %3.4f (s) - Speed Up X%3.3f" % (T[2],T[0]/T[2]))
  if checkTest1(E)==1:
    sys.exit()
  if Verbose: 
    print('-----------------------------------------------------')
    print('  Test 2: Validations by integration on [0,1]x[0,1]  ')
    print('-----------------------------------------------------')
  deg=np.zeros(len(LF))
  E=np.zeros(len(LF))
  for i in range(len(LF)):
    test=TestStiff(LF[i][0],LF[i][1])
    deg[i]=test.du+test.dv
    #U=EvalFunc(test.u,Th.q[:,0],Th.q[:,1])
    #V=EvalFunc(test.v,Th.q[:,0],Th.q[:,1])
    U=test.fu(Th.q[:,0],Th.q[:,1])
    V=test.fv(Th.q[:,0],Th.q[:,1])
    Ifem=numpy.dot(Mbase*U,V)
    E[i]=abs(Ifem-test.I)
    #print("Test %d: u(x,y)=%s, v(x,y)=%s" %(i,test.cu,test.cv))
    #print("  -> error : %e\n" % abs(Ifem-test.I))
    if Verbose: print("    function %d : u(x,y)=%s, v(x,y)=%s,\n           -> Stiff error=%e" % (i,test.cu,test.cv,E[i]) );
  if checkTest2(deg,E)==1:
    sys.exit()
  if Verbose: 
    print('--------------------------------')
    print('  Test 3: Validations by order  ')
    print('--------------------------------')
  LN=range(10,220,20)
  n=len(LN)
  h=np.zeros(n)
  Error=np.zeros(n)
  k=len(LF)-1
  test=TestStiff(LF[k][0],LF[k][1])
  if Verbose: print("Test %d: u(x,y)=%s, v(x,y)=%s" %(k,test.cu,test.cv))
  for i in range(n):
    Th=SquareMesh(LN[i])
    q=Th.q;me=Th.me
    tstart=time.time()
    M=StiffAssembling2DP1OptV2(Th.nq,Th.nme,q,me,Th.areas)
    TT=time.time()-tstart
    U=test.fu(q[:,0],q[:,1])
    V=test.fv(q[:,0],q[:,1])
    Ifem=numpy.dot(M*U,V)
    h[i]=GetMaxLengthEdges(Th.q,Th.me)
    Error[i]=abs(Ifem-test.I)
    if Verbose: 
      print("      Matrix size                      : (%d,%d)" % M.shape)
      print("      StiffAssemblingP1OptV2 CPU times : %3.3f(s)" % TT)
      print("      Error                            : %e" % Error[i]);

  if checkTest3(h,Error)==1:
    sys.exit() 
  if Plot: 
    PlotTest3(h,Error,'Test 3 : Stiffness Matrix (2D/P1)')  