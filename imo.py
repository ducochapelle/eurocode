# some calculations for IMO static stability

from pint import UnitRegistry
import logging
import math

u = UnitRegistry()
logging.basicConfig(level=logging.DEBUG)

'''
+ exec(s)
+ replace("# {", "=> {"
+ If "# {" in line: formatargs.append(split("=")[0])
+ But then also auto-formatting and auto-unit
+ Also add things to summary, so I can print them later
+ Also take care of namespaces by using functions?
+ that way vars don't get reused unexcpectedly
+ Make sure global vars can be used though!

Eurocode.

1. Load factors

LoadFactors(grens, gevolg)

2. Pen gat verbinding

Symmetrisch: PinMidHole(string)
Assymetrisch: PinSideHole(string)

2b. Pen 

Symmetrisch: PinMid(string)
Assymetrisch: PinSide(string)

2a. Gat

Gegeven dikte: HoleB(string)
Suggereerde dikte: HoleA(string)

3. Sections

4. Las verbinding

sigma_vm < fu / beta / ym2

met fu = UTS 
    beta = 0.8 - 1.0: Beta(fu, t)
    ym2  = 1.25
'''

def Header(f, level=4):
    Header_string = '\n## '
    s = 2*Header_string+'{}'+Header_string+'{}'+Header_string
    if   level==1: f = s.format(f.upper(),'='*len(f))
    elif level==2: f = s.format(f.upper(),'-'*len(f))
    elif level==3: f = s.format(f.title(),'='*len(f))
    elif level==4: f = s.format(f.title(),'-'*len(f))
    return f

def execprint(f, extra_units=[]):
    global summary
    execprint_units = [u.dimensionless, u.kN, u.mm, u.mm**2, u.m**3, u.m/u.s, u.kg, u.MPa]
    args = []
    for line in f.splitlines():
        logging.debug(line)
        exec(line)
        if '# => {' in line:
            line1 = line.split('#')[0]
            var = line1.split('=')[0].strip()
            for i in extra_units+execprint_units:
                if (eval(var)/i).unitless:
                    evar = eval(var).to(i)
                    break
            else:
                evar = eval(var)
            args.append(evar)
            if not '=' in line1:
                summary += line.format(evar) + '\n'
            x = False
        if line.startswith("## "):
            summary += line+'\n'
    f = f.format(*args)
    pprint(f)
    return f
        
def pprint(s):
    s = s.replace("*u."  ," ")
    s = s.replace("math.","")
    s = s.replace("# =>" ,"=>")
    s = s.replace(" u.mm","")
    s = s.replace("\n## " ,"\n")
    print(s)

def read_table(key, table):
    for n in range(len(table)//2):
        if key <= table[2*n]:
            break
    else: # over bounds
        return table[2*n+1]
    if n == 0: # under bounds
        return table[2*n+1]
    else: # between bounds -> interpolate
        return    (table[2*n+1] - table[2*n-1]) \
                * (      key    - table[2*n-2]) \
                / (table[2*n+0] - table[2*n-2]) \
                + (table[2*n-1] +       0*n-0 )
  
def Table_X1(B,d):
    return read_table(B/d,[
2.4, 1.0,
2.5, 0.98,
2.6, 0.96,
2.7, 0.95,
2.8, 0.93,
2.9, 0.91,
3.0, 0.90,
3.1, 0.88,
3.2, 0.86,
3.4, 0.82,
3.5, 0.80])

def Table_X2(Cb):
    return read_table(Cb,[
0.45, 0.75,
0.50, 0.82,
0.55, 0.89,
0.60, 0.95,
0.65, 0.97,
0.70, 1.00])

def Table_k(Ak,Lwl,B):
    return read_table(Ak*100/Lwl/b,[
0, 1.0,
1.0, 0.98,
1.5, 0.95,
2.0, 0.88,
2.5, 0.79,
3.0, 0.74,
3.5, 0.72,
4.0, 0.70])

def Table_s(T):
    return read_table(T,[
6, 0.100,
7, 0.098,
8, 0.093,
12, 0.065,
14, 0.053,
16, 0.044,
18, 0.038,
20, 0.035])

#############################
###                       ###
###   START USER SCRIPT   ###
###                       ###
#############################

summary = '' 

f = '''
Lwl = 24.2
B = 5.5
d = 1.35
Cb = 1
KG = 3.2
GM = 1.73

P = 504 # *u.Pa
A = 50 # *u.m**2
Z = 5.5 # *u.m
delta = 73 # *u.t
g = 9.81 # *u.m/u.s**2

l_w1 = P*A*Z/g/delta/1000
l_w2 = 1.5*l_w1

X1 = Table_X1(B, d)
X2 = Table_X2(Cb)
k = 1.0              # no bilge or bar keels
r = 0.73 + 0.6*(KG-d)/d
C = 0.373 + 0.023*(B/d) - 0.043 * (Lwl/100)
T = 2*C*B/GM**.5
s = Table_s(T)

phi1 = 109*k*X1*X2*(r*s)**.5

l_w1 * u.dimensionless # => {:.3f}
l_w2 * u.dimensionless # => {:.3f}
X1 * u.dimensionless # => {:.3f}
X2 * u.dimensionless # => {:.3f}
T * u.dimensionless # => {:.3f}
s * u.dimensionless # => {:.3f}
r * u.dimensionless # => {:.3f}
phi1 * u.dimensionless # => {:.3f}

'''

execprint(f, extra_units=[u.m])

f = '''
Lwl = 24.2*u.m
B = 5.5*u.m
d = 1.35*u.m
Cb = 1
KG = 3.2*u.m
GM = 1.73*u.m

P = 504*u.Pa
A = 50*u.m**2
Z = 5.5*u.m
delta = 73*u.t
g = 9.81*u.m/u.s**2

l_w1 = P*A*Z/g/delta
l_w2 = 1.5*l_w1

X1 = Table_X1(B, d)
X2 = Table_X2(Cb)
k = 1.0              # no bilge or bar keels
r = 0.73 + 0.6*(KG-d)/d
C = 0.373 + 0.023*(B/d) - 0.043 * (Lwl/100/u.m)
T = 2*C*B/GM**.5
s = Table_s(T)

phi1 = 109*k*X1*X2*(r*s)**.5

l_w1 # => {:.3f}
l_w2 # => {:.3f}
X1  # => {:.3f}
X2  # => {:.3f}
T # => {:.3f}
s # => {:.3f}
r # => {:.3f}
phi1 # => {:.3f}

'''

execprint(f, extra_units=[u.m])

#############################
###                       ###
###    END USER SCRIPT    ###
###                       ###
#############################

# redundant safety measure for working with units
assert u.stathenry, 'Variable u is overwritten?'
