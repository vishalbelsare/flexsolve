# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 00:35:01 2019

@author: yoelr
"""
from .exceptions import SolverError
import numpy as np

__all__ = ('false_position', 'bounded_wegstein',
           'bounded_aitken', 'IQ_interpolation')

def false_position(f, x0, x1, y0, y1, x, yval, xtol, ytol):
    """False position solver."""
    _abs = abs
    if y1 < 0.: x0, y0, x1, y1 = x1, y1, x0, y0
    dx = x1-x0
    dy = yval-y0
    if not (x0 < x < x1 or x1 < x < x0):
        x = x0 + dy*dx/(y1-y0)
    yval_ub = yval + ytol
    yval_lb = yval - ytol
    x_old = x
    while _abs(dx) > xtol:
        y = f(x)
        if y > yval_ub:
            x1 = x
            y1 = y
        elif y < yval_lb:
            x0 = x
            y0 = y
            dy = yval-y
        else: break
        dx = x1-x0
        x = x0 + dy*dx/(y1-y0)
        if _abs(x - x_old) < dx/10: x = (x1 + x0)/2.
    return x

def IQ_interpolation(f, x0, x1, y0, y1, x, yval, xtol, ytol):
    """Inverse quadratic interpolation solver."""
    _abs = abs
    if y1 < 0.: x0, y0, x1, y1 = x1, y1, x0, y0
    dx1 = dx0 = x1-x0
    f0 = yval-y0
    if not (x0 < x < x1 or x1 < x < x0):
        dy = y1-y0
        if dy:
            # False position
            x = x0 + f0*dx0/dy
            if not (x0 < x < x1 or x1 < x < x0):
                x = (x0+x1)/2
        else:
            # Bisection
            x = (x0+x1)/2
    yval_ub = yval + ytol
    yval_lb = yval - ytol
    while _abs(dx1) > xtol:
        y = f(x)
        if y > yval_ub:
            y2 = y1
            x2 = x1
            x1 = x
            y1 = y
        elif y < yval_lb:
            y2 = y0
            x2 = x0
            x0 = x
            y0 = y
            f0 = yval-y
        else: break
        dx1 = x1-x0
        try:
            # Inverse quadratic interpolation
            f1 = yval - y1
            f2 = yval - y2
            d01 = f0-f1
            d02 = f0-f2
            d12 = f1-f2
            f0_d12 = f0/d12
            f1_d02 = f1/d02
            f2_d01 = f2/d01
            x = x0*f1_d02*f2_d01 - x1*f0_d12*f2_d01 + x2*f0_d12*f1_d02
            if not (x0 < x < x1 or x1 < x < x0):
                x = (x0+x1)/2
        except:
            dy = y1-y0
            if dy:
                # False position
                x = x0 + f0*dx1/dy
                if (x0 < x < x1 or x1 < x < x0):
                    # Overshoot to prevent getting stuck
                    x = x + 0.1*(x1 + x0 - 2.*x)*(dx1/dx0)**3
                else:
                    # Bisection
                    x = (x0+x1)/2
            else:
                x = (x0+x1)/2    
        dx0 = dx1
    return x

def bounded_wegstein(f, x0, x1, y0, y1, x, yval, xtol, ytol):
    """False position solver with Wegstein acceleration."""
    _abs = abs
    if y1 < 0.: x0, y0, x1, y1 = x1, y1, x0, y0
    dy = yval-y0
    x_old = x = x if x0 < x < x1 or x1 < x < x0 else x0+dy*(x1-x0)/(y1-y0)
    y = f(x)
    yval_ub = yval + ytol
    yval_lb = yval - ytol
    if y > yval_ub:
        x1 = x
        y1 = y
    elif y < yval_lb:
        x0 = x
        y0 = y
        dy = yval - y
    else:
        return x
    dx1x0 = x1-x0
    x = g0 = x0 + dy*dx1x0/(y1-y0)
    while _abs(dx1x0) > xtol:
        y = f(x)
        if y > yval_ub:
            x1 = x
            y1 = y
        elif y < yval_lb:
            x0 = x
            y0 = y
            dy = yval - y
        else: break
        dx1x0 = x1-x0
        g1 = x0 + dy*dx1x0/(y1-y0)
        dx = x - x_old
        try:
            w = dx/(dx-g1+g0)
            x_old = x
            x = w*g1 + (1.-w)*x
        except:
            x = g0 = g1
        else:
            if x0 < x < x1 or x1 < x < x0: g0 = g1                
            else: x = g0 = g1
    return x
       
def bounded_aitken(f, x0, x1, y0, y1, x, yval, xtol, ytol):
    """False position solver with Aitken acceleration."""
    _abs = abs
    if y1 < 0.: x0, y0, x1, y1 = x1, y1, x0, y0
    dx1 = x1-x0
    dy = yval-y0
    if not (x0 < x < x1 or x1 < x < x0):
        x = x0 + dy*dx1/(y1-y0)
    yval_ub = yval + ytol
    yval_lb = yval - ytol
    while _abs(dx1) > xtol:
        y = f(x)
        if y > yval_ub:
            x1 = x
            y1 = y
        elif y < yval_lb:
            x0 = x
            y0 = y
            dy = yval-y
        else: 
            return x
        dx0 = x1-x0
        g = x0 + dy*dx0/(y1-y0)
        if _abs(dx0) < xtol:
            return g
        
        y = f(g)
        if y > yval_ub:
            x1 = g
            y1 = y
        elif y < yval_lb:
            x0 = g
            y0 = y
            dy = yval-y
        else:
            return g
        dx1 = x1-x0
        gg = x0 + dy*dx1/(y1-y0)
        dxg = x - g
        try: x = x - dxg**2./(gg + dxg - g)
        except:
            # Add overshoot to prevent getting stuck
            x = gg + 0.1*(x1+x0-2*gg)*(dx1/dx0)**3. 
        else:
            if not (x0 < x < x1 or x1 < x < x0):
                x = gg + 0.1*(x1+x0-2*gg)*(dx1/dx0)**3. 
    return x