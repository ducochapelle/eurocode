from math import sin, cos, tan, asin, acos, atan
from math import degrees, radians, pi
# from pint import UnitRegistry
# u = UnitRegistry()

# input 
def Pinhole(   Q=None,
                        G=None,
                        fy=None,
                        fup=None,
                        fyp=None,
                        tB=None,
                        d0B=None,
                        Fed=None,
                        ym_0=1,
                        ym_2=1.25,
                        ym_6=1,
                        E=210000,
                        _0=0.03,
                        cp=2):
    if Fed == None:
        Fed = (Q*1.5+G*1.35)
    else:
        assert Q==None and G==None, "Q G or Fed!"

    typeA = tB == None and d0B == None
    typeB = tB != None and d0B != None
    assert typeA or typeB, "tB and d0B!"
    tA	=	0.7*(Fed*ym_0/fy)**.5
    d0A	=	2.5*tA
    aA	=	1.1*d0A
    cA	=	0.75*d0A
    if typeA:
        tB  = tA
        d0B = d0A
        aB  = aA
        cB  = cA
    elif typeB:                    
        aB	=	Fed*ym_0/2/tB/fy+2*d0B/3
        cB	=	Fed*ym_0/tB/fy/2+d0B/3        
    wB	=	d0B+2*cB
    eB	=	aB-cB
    rB	=	d0B/2+aB
        
    # pin prep

    dP	=	round(d0B*(1-_0)) # 0.5*mm fuck this
    σhEd    =	0.591*((E*Fed*(d0B-dP))/(dP**2*tB))**.5
    Med	=	Fed/8*(tB+4*cp+2*tB/2)
    A	=	pi/4*dP**2
    W	=	pi/4*(dP/2)**4*2/dP

    # pin capacities
                    
    FvRd    =	0.6*A*fup/ym_2
    FbRd    =	1.5*tB*dP*fy/ym_0
    FbRd_ser=	0.6*tB*dP*fy/ym_6
    MRd	=	1.5*W*fyp/ym_0
    MRd_ser =	0.8*W*fyp/ym_6
    FhRd    =	2.5*fy/1.1

    # unit checks
                    
    csh	=	Fed/FvRd
    cbr	=	Fed/FbRd
    cbn	=	Med/MRd
    ccm	=	cbn**2+csh**2
    sbr	=	Fed/FbRd_ser
    sbn	=	Med/MRd_ser
    shz	=	σhEd/FhRd

    # godverkanker
    a = [csh, cbr, cbn, ccm, sbr, sbn, shz, tB, d0B, rB, dP, Fed]
    s = "csh, cbr, cbn, ccm, sbr, sbn, shz, t, d, R, D, F, ".replace(", ",":{} ")
    return [s]+a
