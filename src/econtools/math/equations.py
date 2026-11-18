"""
Math formatting and printing functions
"""

import numpy as np
from sympy import nsimplify

def sign(x):
    # Returns '+' if x is positive, '-' if x is negative, and '' if x is zero
    if x > 0: 
        return '+'
    elif x < 0:
        return '-'
    else:
        return ''

def is_rational(x, maxdenom=8):
    try:
        d = nsimplify(x).q
        return (d <= maxdenom)
    except:
        return False

def asfrac(x, inline=False, maxdenom=8, rmplus=True, rmneg=False):
    # Returns the string representation of x as a fraction
    if not is_rational(x, maxdenom):
        return f'{x:g}'
    d = nsimplify(x).q
    n = np.abs(nsimplify(x).p)
    out = sign(x)
    if d==1: out+=f'{n}'
    elif inline: out+=fr'{n}/{d}'
    else: out+=fr'\frac{{{n}}}{{{d}}}'
    if out[0]=='+' and rmplus: out=out[1:]
    elif out[0]=='-' and rmneg: out=out[1:]
    return out
    
class PTerm:
    # Represents a term in a polynomial equation
    # c: coefficient
    # x: variable symbol
    # p: power
    def __init__(self,c=1,x='x',p=0.5):
        # Initializes the term
        self.c = c
        self.x = x
        self.p = p
    def print(self, maxdenom=8, rmplus=True, rmneg=False):
        # Returns the string representation of the term
        c = asfrac(self.c, inline=False, maxdenom=maxdenom, rmplus=rmplus, rmneg=rmneg)
        p = asfrac(self.p, inline=True, maxdenom=maxdenom, rmplus=True, rmneg=False)
        if self.c==0: return ''
        if self.p==0: return c
        if self.p==1: xp = fr'{self.x}'
        else: xp = fr'{self.x}^{{{p}}}'
        if self.c==-1: out = fr'-{xp}'
        elif self.c==1: out = fr'+{xp}'
        else: out = fr'{c}{xp}'
        if out[0]=='+' and rmplus: out=out[1:]
        elif out[0]=='-' and rmneg: out=out[1:]
        return out
    def __repr__(self):
        return self.print()

class PolyEq:
    # Represents a polynomial equation
    # c: coefficients
    # x: variable symbol
    # p: powers
    def __init__(self, c=[1,1,1], x='x', p=[0,1,2]):
        # Initializes the polynomial equation
        assert len(c)==len(p)
        assert type(x)==str or len(x)==len(c)
        if type(x)==str:
            x = [x]*len(c)
        self.c = c
        self.x = x
        self.p = p
    def print(self, maxdenom=8, rmplus=True, rmneg=False):
        # Returns the string representation of the polynomial equation
        out = ''
        for i in range(len(self.c)):
            pterm = PTerm(self.c[i], self.x[i], self.p[i])
            out+=fr'{pterm.print(maxdenom=maxdenom, rmplus=False, rmneg=False)}'
        if out[0]=='+' and rmplus: out=out[1:]
        elif out[0]=='-' and rmneg: out=out[1:]
        return out
    def __repr__(self):
        return self.print()
