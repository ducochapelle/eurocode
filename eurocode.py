from member.member import *
from pint import UnitRegistry
import math
u = UnitRegistry()

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

3. Las verbinding

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

def PinMidHole(f):
    return PinHole(PinMid(f))

def PinSideHole(f):
    return PinHole(PinSide(f))

def PinHole(f):
    return f + HoleB('''
Fed = FbEd1 # => {:.0f~}
t   = a1
d0  = d*1.03''') + HoleB('''
Fed = FbEd # => {:.0f~}
t   = b
d0  = d*1.03''') + HoleB('''
Fed = FbEd2 # => {:.0f~}
t   = a2
d0  = d*1.03''')

def PinMid(f):
    return Pin(f+'''
#
#    | FbEd1       Λ FbEd      | FbEd2
#    V             | = Fed     V
#   
# |-a1-|   c1   |--b---| c2 |-a2-|
#
L1= (2*a1+b+4*c1)/4
L2= (2*a2+b+4*c2)/4
FvEd1 = Fed * L2/(L1+L2) # => {:.0f~}
FvEd2 = Fed * L1/(L1+L2) # => {:.0f~}
FvEd = max(FvEd1,FvEd2)
M_Ed  = L1*FvEd1''')

def PinSide(f):
    return Pin(f+'''
#
#    | FbEd1       Λ FbEd      | FbEd2
#    V = Fed       |           V
#   
# |-a1-|   c1   |--b---| c2 |-a2-|
#
L1= (2*a1+b+4*c1)/4
L2= (2*a2+b+4*c2)/4
FvEd1 = Fed         # => {:.0f~}
FvEd2 = Fed * L1/L2 # => {:.0f~}
FvEd = max(FvEd1,FvEd2)
M_Ed  = L1*FvEd1''')

def Pin(f):
    return Header("Pin")+f+'''
fy = min(fy, fyp)
A = math.pi/4*d**2 
W = math.pi/32*d**3

FvRd = 0.6*A*fup/ym2
M_Rd = 1.5*W*fyp/ym0

FvEd / FvRd # => {:.2f~}
M_Ed / M_Rd # => {:.2f~}
((M_Ed/M_Rd)**2+(FvEd/FvRd)**2)**.5 # => {:.2f~}

FbEd1 = FvEd1  # => {:.0f~}
FbEd2 = FvEd2 # => {:.0f~}
FbEd  = FvEd1 + FvEd2 # => {:.0f~}
FbRd1 = 1.5*a1*d*fy/ym0
FbRd2 = 1.5*a2*d*fy/ym0
FbRd  = 1.5*b*d*fy/ym0

FbEd / FbRd # => {:.2f~}
FbEd1 / FbRd1 # => {:.2f~}
FbEd2 / FbRd2 # => {:.2f~}'''
 
def HoleB(f):
    return Header("Hole B")+f+'''
a = Fed*ym0/2/t/fy + 2/3*d0
c = a - 1/3*d0
R = d0/2 + c
e = a-c
t  # => {:.0f~}
d0 # => {:.0f~}
R  # => {:.0f~}
e  # => {:.0f~}'''
    
def HoleA(f):
    return Header("Hole A")+f+'''
t = 0.7*(Fed*ym0/fy)**.5 
d0= 2.5*t 
R = 1.25*d0 
e = 0.3*d0 
t  # => {:.0f~}
d0 # => {:.0f~}
R  # => {:.0f~}
e  # => {:.0f~}'''

summary = Header('summary',level=1)

partialfactors = '''
ym0 = 1
ym1 = 1
ym2 = 1.25'''

f = HoleB('''
Fed= 1000*u.kN
fy = 220*u.MPa
d0 = 20*u.mm
t  = 10*u.mm
ym0= 1''')

f += HoleA('''
Fed= 1000*u.kN
fy = 220*u.MPa
ym0= 1''')

f += PinMid(partialfactors+'''
Fed= 3000*u.kN
fy = 220*u.MPa
fyp= 300*u.MPa
fup= 400*u.MPa
d  = 20*u.mm
a1 = 5*u.mm
a2 = 10*u.mm
b  = 15*u.mm
c1 = 20*u.mm
c2 = 10*u.mm''')

f = Header("Nou hier gebeurt het hoor!", level=1)
f += PinMidHole(partialfactors+'''
Fed= 100*u.kN
fy = 220*u.MPa
fyp= 300*u.MPa
fup= 400*u.MPa
d  = 20*u.mm
a1 = 20*u.mm
a2 = 20*u.mm
b  = 40*u.mm
c1 = 20*u.mm
c2 = 10*u.mm''')

execprint(f)#, extra_units=[u.N]) # holy fuck the unitless gaan over de zeik hier
pprint(summary)


def LoadFactors(grens, gevolg):
    '''
    grens = EQU or STR or GEO
    gevolg = CC1 or CC2 or CC3
     |
     |  Load factors for Eurocode
     V
    yg = factor on own mass
    yg_ = factor on favourable own mass
    yq = factor on load
    '''
    data = {"EQU":{"CC1":(1.,  .9, 1.35),
                   "CC2":(1.1, .9, 1.5 ),
                   "CC3":(1.2, .9, 1.65)},
            "STR":{"CC1":(1.2, .9, 1.35),
                   "CC2":(1.35,.9, 1.5 ),
                   "CC3":(1.5, .9, 1.65)},
            "GEO":{"CC1":(1.2, .9, 1.35),
                   "CC2":(1.35,.9, 1.5 ),
                   "CC3":(1.5, .9, 1.65)}}
    yg,ygn,yq = data[grens][gevolg]
    return yg,yg_,yq

def Beta(fu, t):
    '''
    fu = ultimet tensile stress
    t = material thickness
     |
     |  Weld factor for Eurocode
     V
    Beta = weld factor
    '''
    if t > 40: 
        k = 1/1.1
    elif t <=100:
        k = 1.
    else:
        assert false, "Beta t out of bounds"
    if   fu <= 360: return 0.80*k
    elif fu <= 430: return 0.85*k
    elif fu <= 510: return 0.90*k
    elif fu <= 520: return 1.00*k
    elif fu <= 540: return 1.00*k
    else: return 1.00

# redundant safety measure for working with units
assert u.stathenry, 'Variable u is overwritten?'
