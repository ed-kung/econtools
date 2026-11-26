"""
Scaled numbers for auto generated econ problems

A scaled number is a (grid value) x (scale factor).
Arithmetic operatiosn are performed on grid values, and scale factors are applied to the result.

Example:
p = Scaled()
"""

from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from numbers import Real
import numpy as np

Num = Fraction | float   # exact when possible, float otherwise

def _exact_or_float(x) -> Num:
    # Keep floats as floats; turn ints, Fractions, annd strings into Fractions
    if isinstance(x, float):
        return x
    else:
        return Fraction(x)

NUMTYPES = ('', '$', '%')

def _check_numtype(numtype: str) -> None:
    if numtype not in NUMTYPES:
        raise ValueError(f"numtype must be one of {NUMTYPES}, got {numtype!r}")

def _human(x: Num) -> str:
    # Human readable representation with k/m/B/T suffixes
    v = float(x)
    for size, suffix in ((1e12, 'T'), (1e9, 'B'), (1e6, 'm'), (1e3, 'k')):
        if abs(v) >= size:
            return f"{v/size:,g}{suffix}"
    return f"{v:,g}"

def format_number(x: Num, numtype: str = '', human: bool = True) -> str:
    # Display string for a number:
    #   numtype '$': '$' prefix (sign goes in front: -$5)
    #   numtype '%': value converted to a percentage with '%' suffix; never uses k/m/B/T
    #   human: use k/m/B/T suffixes (ignored for '%'); otherwise plain thousands separators
    _check_numtype(numtype)
    v = float(x)
    if numtype == '%':
        v *= 100
        human = False
    sign = '-' if v < 0 else ''
    v = abs(v)
    s = _human(v) if human else f"{v:,g}"
    if numtype == '$':
        s = '$' + s
    elif numtype == '%':
        s = s + '%'
    return sign + s

def _combine(a: str, b: str) -> str:
    # numtype of a result: shared numtype, or the one that is set; '' if they conflict
    if a == b or not b:
        return a
    if not a:
        return b
    return ''

def _equals(a: Num, b: Num) -> bool:
    # Exact comparison or within tolerance
    if isinstance(a, float) or isinstance(b, float):
        return np.abs(a - b) < 1e-6
    return a == b

@dataclass(frozen=True)
class Scaled:
    grid: Num              # grid value on a graph
    scale: Num = 1         # scale factor (what one grid tick is worth)
    numtype: str = ''      # '' (plain), '$' (dollar prefix), or '%' (percentage with % suffix)

    def __post_init__(self):
        _check_numtype(self.numtype)
        # ints/Fractions/strings -> exact Fraction; floats stay floats
        object.__setattr__(self, "grid", _exact_or_float(self.grid))
        object.__setattr__(self, "scale", _exact_or_float(self.scale))
    
    @property
    def real(self) -> Num:
        # real world value: grid * scale
        return self.grid * self.scale
    
    @staticmethod
    def _coerce(other) -> Scaled:
        if isinstance(other, Scaled):
            return other
        if isinstance(other, Real):
            return Scaled(other, 1)
        return NotImplemented
    
    # Multiplication
    def __mul__(self, other):
        o = self._coerce(other)
        if o is NotImplemented:
            return o
        return Scaled(self.grid * o.grid, self.scale * o.scale, _combine(self.numtype, o.numtype))
    __rmul__ = __mul__

    # Division
    def __truediv__(self, other):
        o = self._coerce(other)
        if o is NotImplemented:
            return o
        return Scaled(self.grid / o.grid, self.scale / o.scale, _combine(self.numtype, o.numtype))
    
    def __rtruediv__(self, other):
        o = self._coerce(other)
        if o is NotImplemented:
            return o
        return o / self
    
    # Powers
    def __pow__(self, n):
        return Scaled(self.grid ** n, self.scale ** n, self.numtype)

    # Negation
    def __neg__(self):
        return Scaled(-self.grid, self.scale, self.numtype)
    
    # Addition and subtraction 
    def _from_real(self, real: Num, o: Scaled) -> Scaled:
        scale = max(self.scale, o.scale)
        return Scaled(real / scale, scale, _combine(self.numtype, o.numtype))
    
    def __add__(self, other):
        o = self._coerce(other)
        if o is NotImplemented:
            return o
        return self._from_real(self.real + o.real, o)
    __radd__ = __add__

    def __sub__(self, other):
        o = self._coerce(other)
        if o is NotImplemented:
            return o
        return self._from_real(self.real - o.real, o)
    
    def __rsub__(self, other):
        o = self._coerce(other)
        if o is NotImplemented:
            return o
        return o - self
    
    # Comparison
    def __eq__(self, other):
        o = self._coerce(other)
        if o is NotImplemented:
            return o
        return self.real == o.real
    
    def __hash__(self):
        return hash(self.real)
    
    def __lt__(self, other):
        o = self._coerce(other)
        if o is NotImplemented:
            return o
        return self.real < o.real
    
    def __le__(self, other):
        o = self._coerce(other)
        if o is NotImplemented:
            return o
        return self.real <= o.real

    def __gt__(self, other):
        o = self._coerce(other)
        if o is NotImplemented:
            return o
        return self.real > o.real

    def __ge__(self, other):
        o = self._coerce(other)
        if o is NotImplemented:
            return o
        return self.real >= o.real

    def isclose(self, other, tol=1e-6) -> bool:
        o = self._coerce(other)
        if o is NotImplemented:
            return o
        return np.isclose(self.real, o.real, atol=tol)
    
    # Display
    def __repr__(self):
        if self.numtype:
            return f"Scaled({self.grid}, {self.scale}, {self.numtype!r})"
        return f"Scaled({self.grid}, {self.scale})"

    def __str__(self):
        return format_number(self.real, self.numtype, human=True)

    def texify(self):
        return format_number(self.real, self.numtype, human=True).replace('$', '\\$').replace('%', '\\%')


# ---- Demo

if __name__ == "__main__":
    PSCALE = 5
    QSCALE = 1_000_000

    p = Scaled(3, PSCALE)
    q = Scaled(4, QSCALE)
    rev = p*q

    print("p      = ", repr(p), " -> ", p)
    print("q      = ", repr(q), " -> ", q)
    print("p*q    = ", repr(rev), " -> ", rev)

    print("")

    x = Scaled(4, 3)
    y = Scaled(3, 4)
    print("x      = ", repr(x), " -> ", x)
    print("y      = ", repr(y), " -> ", y)
    print("x==y   = ", x == y)



    
    




