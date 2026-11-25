import numpy as np
from econtools.graphs.primitives import Point, Line
from econtools.math.equations import PolyEq

class LinearDemand:
    # p = a - b*q
    # q = (a/b) - (1/b)*p
    def __init__(self, a=12, b=1, **kwargs):
        assert a > 0
        assert b > 0
        self.a = a
        self.b = b
        self.line = Line(-b, a, **kwargs)
    def print(self, x='p', maxdenom=8):
        return PolyEq(c=[self.a/self.b, -1/self.b], x=x, p=[0,1]).print(maxdenom=maxdenom, rmplus=True)
    def print_inverse(self, x='q', maxdenom=8):
        return PolyEq(c=[self.a, -self.b], x=x, p=[0,1]).print(maxdenom=maxdenom, rmplus=True)
    def eval_at_p(self, p):
        return self.a/self.b - (1/self.b)*p
    def eval_at_q(self, q):
        return self.a - self.b*q
    def plot(self, ax):
        return self.line.plot(ax)
    @classmethod
    def from_points(cls, point1 : Point, point2 : Point, **kwargs):
        if np.isclose(point1.x, point2.x) and np.isclose(point1.y, point2.y):
            raise ValueError("Points are the same")
        slope = (point2.y - point1.y) / (point2.x - point1.x)
        intercept = point1.y - slope*point1.x
        return cls(a=intercept, b=-slope, **kwargs)

class LinearSupply:
    # p = a + b*q
    # q = (1/b)*p - (a/b)
    def __init__(self, a=1, b=1, **kwargs):
        assert a >= 0
        assert b >= 0
        self.a = a
        self.b = b
        self.line = Line(b, a, **kwargs)
    def print(self, x='p', maxdenom=8):
        return PolyEq(c=[1/self.b, -a/self.b], x=x, p=[1,0]).print(maxdenom=maxdenom, rmplus=True)
    def print_inverse(self, x='q', maxdenom=8):
        return PolyEq(c=[self.a, self.b], x=x, p=[0,1]).print(maxdenom=maxdenom, rmplus=True)
    def eval_at_p(self, p):
        if self.b > 0:
            return (1/self.b)*p - (self.a/self.b)
        else:
            return np.inf
    def eval_at_q(self, q):
        return self.a + self.b*q
    def plot(self, ax):
        return self.line.plot(ax)
    @classmethod
    def from_points(cls, point1 : Point, point2 : Point, **kwargs):
        if np.isclose(point1.x, point2.x) and np.isclose(point1.y, point2.y):
            raise ValueError("Points are the same")
        slope = (point2.y - point1.y) / (point2.x - point1.x)
        intercept = point1.y - slope*point1.x
        return cls(a=intercept, b=slope, **kwargs)

class LinearMarket:
    # Demand: p = demand.a - demand.b*q
    # Supply: p = supply.a + supply.b*q
    # equilibrium_quantity = (demand.a - supply.a) / (demand.b + supply.b)
    def __init__(self, demand : LinearDemand, supply : LinearSupply):
        self.demand = demand
        self.supply = supply
        q = (demand.a - supply.a) / (demand.b + supply.b)
        p1 = demand.eval_at_q(q)
        p2 = supply.eval_at_q(q)
        assert np.isclose(p1, p2)
        p = p1
        CS = 0.5*(demand.a - p)*q
        PS = 0.5*(p - supply.a)*q
        self.eq = {'q':q, 'p':p, 'CS':CS, 'PS':PS, 'TS':CS+PS}
    @classmethod
    def from_points(cls, demand_point : Point, supply_point : Point, equilibrium : Point):
        demand = LinearDemand.from_points(demand_point, equilibrium)
        supply = LinearSupply.from_points(supply_point, equilibrium)
        return cls(demand, supply)



