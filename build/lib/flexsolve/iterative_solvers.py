# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 22:57:42 2019

@author: yoelr
"""
from .exceptions import SolverError
import numpy as np

__all__ = ('wegstein', 'conditional_wegstein', 
           'aitken', 'conditional_aitken')

def wegstein(f, x0, xtol, args=(), maxiter=50):
    """Iterative Wegstein solver."""
    x1 = g0 = f(x0, *args)
    w = np.ones_like(x0)
    np_abs = np.abs
    for iter in range(maxiter):
        dx = x1-x0
        try: g1 = f(x1, *args)
        except:
            x1 = g1
            g1 = f(x1, *args)
        if (np_abs(g1-x1) < xtol).all(): return g1
        dummy = dx-g1+g0
        mask = np_abs(dummy) > 1e-16
        w[mask] = dx[mask]/dummy[mask]
        x0 = x1
        g0 = g1
        x1 = w*g1 + (1-w)*x1
    raise SolverError(f'failed to converge after {maxiter} iterations')

def conditional_wegstein(f, x0):
    """Conditional iterative Wegstein solver."""
    g0, condition = f(x0)
    g1 = x1 = g0
    w = np.ones_like(x0)
    np_abs = np.abs
    while condition:
        try: g1, condition = f(x1)
        except:
            x1 = g1
            g1, condition = f(x1)
        dx = x1-x0
        dummy = dx-g1+g0
        mask = np_abs(dummy) > 1e-16
        w[mask] = dx[mask]/dummy[mask]
        x0 = x1
        g0 = g1
        x1 = w*g1 + (1.-w)*x1

def aitken(f, x, xtol, args=(), maxiter=50):
    """Iterative Aitken solver."""
    gg = x
    x = x.copy()
    abs_ = abs
    np_abs = np.abs
    for iter in range(maxiter):
        try: g = f(x, *args)
        except:
            x = gg.copy()
            g = f(x, *args)
        dxg = x - g
        if (abs_(dxg) < xtol).all(): return g
        gg = f(g, *args)
        dgg_g = gg - g
        if (abs_(dgg_g) < xtol).all(): return gg
        dummy = dgg_g + dxg
        mask = np_abs(dummy) > 1e-16
        x[mask] -= dxg[mask]**2/dummy[mask]
    raise SolverError(f'failed to converge after {maxiter} iterations')
    
def conditional_aitken(f, x):
    """Conditional iterative Aitken solver."""
    condition = True
    x = x.copy()
    gg = x
    np_abs = np.abs
    while condition:
        try:
            g, condition = f(x)
        except:
            x = gg.copy()
            g, condition = f(x)
        if not condition: return g
        gg, condition = f(g)
        dxg = x - g
        dummy = gg + dxg - g
        mask = np_abs(dummy) > 1e-16
        x[mask] -= dxg[mask]**2/dummy[mask]