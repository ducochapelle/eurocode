from pint import UnitRegistry
import logging
import math

u = UnitRegistry()
logging.basicConfig(level=logging.INFO)

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

def Stability(f):
    '''A, I, E, L, fy, a, yM1'''
    return Header("Stability")+f+'''
Ny  = A*fy           # => {:.0f~}
Ncr = math.pi**2*E*I/L**2 # => {:.0f~}
λ   = (A*fy/Ncr)**.5
φ   = 0.5*(1+a*(λ-0.2)+λ**2)
χ   = 1/(φ+(φ**2-λ**2)**.5)
NbRd= χ*A*fy/ym1     # => {:.0f~}'''

def Stability_FE_DNV(f):
    '''kg, σR, fy, γm, γf -> Rd
	kg	= load multiplier
	σR 	= stress occurring at buckle
	fy 	= yield stress
	γm 	= material factor
	γf      = load factor
	'''
    return Header('Stability FE DNV')+f+'''
λ 	= (fy / σR / kg)**.5
φ	= 0.5*(1 + 0.5*(λ - 0.2) + λ**2)
κ 	= 1/(φ + (φ**2 - λ**2)**.5)
λ # => {:.2f~}
φ # => {:.2f~}
κ # => {:.2f~}
Rd 	= κ * fy * γf / γm / σR # => {:.2f~}'''

def FatigueSN(f):
    '''fy, n'''
    return Header('Fatigue')+f+'''
α = min(n,1e8)
β = 3 if n < 5e2 else 5
fy * (α/2e6) ** (-1/β) # => {:.0f~}'''

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
#    | FbEd1       ^ FbEd      | FbEd2
#    V             | = Fed     V
#   
# |-a1-|   c1   |--b---| c2 |-a2-|
#
L1= (2*a1+b+4*c1)/4
L2= (2*a2+b+4*c2)/4
FvEd1 = Fed * L2/(L1+L2) # => {:.0f~}
FvEd2 = Fed * L1/(L1+L2) # => {:.0f~}
FvEd = max(FvEd1,FvEd2)
M_Ed  = L1*FvEd1 # => {:.0f~}''')

def PinSide(f):
    return Pin(f+'''
#
#    | FbEd1       ^ FbEd      | FbEd2
#    V = Fed       |           V
#   
# |-a1-|   c1   |--b---| c2 |-a2-|
#
L1= (2*a1+b+4*c1)/4
L2= (2*a2+b+4*c2)/4
FvEd1 = Fed         # => {:.0f~}
FvEd2 = Fed * L1/L2 # => {:.0f~}
FvEd = max(FvEd1,FvEd2)
M_Ed  = L1*FvEd1 # => {:.0f~}''')

def Pin(f):
    return Header("Pin")+f+'''
fy = min(fy, fyp)
A = math.pi/4*d**2 
W = math.pi/32*d**3

FvRd = 0.6*A*fup/ym2 # => {:.0f~}
M_Rd = 1.5*W*fyp/ym0 # => {:.0f~}

FvEd / FvRd # => {:.2f~}
M_Ed / M_Rd # => {:.2f~}
((M_Ed/M_Rd)**2+(FvEd/FvRd)**2)**.5 # => {:.2f~}

FbEd1 = FvEd1 # => {:.0f~}
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

def Bar(f):
    '''t -> A I'''
    return Header('Bar')+f+'''
A = t**2      # => {:.2e~}
I = 1/12*t**4 # => {:.2e~}'''

def Rod(f):
    '''D -> A I'''
    return Header('Rod')+f+'''
r = D/2
A = math.pi*r**2   # => {:.2e~}
I = math.pi/4*r**4 # => {:.2e~}'''

def RoundTube(f):
    '''D, t'''
    return Header('Round Tube')+f+'''
Ro = D/2
Ri = D/2-t
A  = math.pi*(Ro**2-Ri**2)   # => {:.2e~}
I  = math.pi/4*(Ro**4-Ri**4) # => {:.2e~}'''

def SquareTube(f):
    '''D, t'''
    return Header('Square Tube')+f+'''
Do = D
Di = D-2*t
A  = Do**2-Di**2      # => {:.2e~}
I  = (Do**4-Di**4)/12 # => {:.2e~}'''

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

#############################
###                       ###
###   START USER SCRIPT   ###
###                       ###
#############################

summary = Header('summary',level=1)

PARTIAL_FACTORS = '''
ym0 = 1
ym1 = 1
ym2 = 1.25'''

STEEL = '''
E = 210*u.GPa
rho = 7860*u.kg/u.m**3
'''

f = PARTIAL_FACTORS

f += Header('Scharnier Boven', level=2)
f += PinSideHole('''
Fed= 1900*u.kN
fy = 335*u.MPa
fyp= 1080*u.MPa
fup= 635*u.MPa
d  = 220*u.mm
a1 = 120*u.mm
a2 = 20*u.mm
b  = 60*u.mm
c1 = 310*u.mm
c2 = 420*u.mm''')

f += Header('Cylinder verbinding', level=2)
f += PinMidHole('''
Fed = 1.5*1500*u.kN
fy  = 335*u.MPa
fyp = 1080*u.MPa
fup = 635*u.MPa
d   = 160*u.mm
a1 = a2 = 20*u.mm
a2  = 20*u.mm
b   = 110*u.mm
c1 = c2 = 175*u.mm''')

execprint(f, extra_units=[u.kN*u.m]) # holy fuck the unitless gaan over de zeik hier
pprint(summary)

f = PARTIAL_FACTORS
f += STEEL
f += Stability('''
A = 1.71E+04*u.mm**2
I = 2.32E+08*u.mm**4
L = 10*u.m
a = 0.34
fy= 355*u.MPa''')

f += FatigueSN('''
fy = 160*u.MPa
n  = 5e5''')

execprint(f)


f = Header('Bucket', level=1)
f += Header('Weld partial pen 40, F G', level=3)
f += RoundTube('''
D = 200*u.mm
t = 40*u.mm''')
f += '''

F = 7.11e5*u.N
L = 50*u.mm

τ = F / A     # => {:.0f~}
σ = F*L*D/2/I # => {:.0f~}
σ_vm = (σ**2 + 3*τ**2)**.5
fy = 355*u.MPa
1.5*σ_vm/fy # => {:.2f~}'''

f += Header('Hinge 1, D E', level=3)

f += Rod('''
D = 200*u.mm''')
f += '''

F = 5.45e5*u.N
L = 50*u.mm

τ = F / A     # => {:.0f~}
σ = F*L*D/2/I # => {:.0f~}
σ_vm = (σ**2 + 3*τ**2)**.5
fy = 355*u.MPa
1.5*σ_vm/fy # => {:.2f~}'''

f += Header('Hinge 2, A', level=3)

f += Rod('''
D = 200*u.mm''')
f += '''

F = 4.19e5*u.N
L = 50*u.mm

τ = F / A     # => {:.0f~}
σ = F*L*D/2/I # => {:.0f~}
σ_vm = (σ**2 + 3*τ**2)**.5
fy = 355*u.MPa
1.5*σ_vm/fy # => {:.2f~}'''

execprint(f)


f = Stability_FE_DNV('''
kg = 36.6
σR = 20*u.MPa
fy = 355*u.MPa
γm = 1.15
γf = 1.3''')

execprint(f)


#############################
###                       ###
###    END USER SCRIPT    ###
###                       ###
#############################

# redundant safety measure for working with units
assert u.stathenry, 'Variable u is overwritten?'
