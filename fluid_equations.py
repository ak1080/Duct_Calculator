import numpy as np
from scipy.optimize import fsolve

GRAVITY = 32.174 # ft/s^2

def reynolds_num(density, velocity, diam, dyn_visc):
    """Simple function to calculate Reynolds number of the air"""
    reynolds = (density * velocity * diam) / (dyn_visc / 3600) #3600 is a conversion factor for viscosity
    return reynolds

def darcy_weisbach(f, velocity, diam, density):
    """Calculates the pressure loss in inWC per 100 ft of straight duct."""
    darcy_weisbach = round((f * 100 * density * velocity ** 2 * 12) / (diam * 2 * GRAVITY * 62.4),3)
    return darcy_weisbach

def colebrook_white_solver_fsolve(re, epsilon, diam, initial_guess=0.02):
    """ Solves the Colebrook-White equation for the Darcy-Weisbach friction factor using fsolve (numerical method)."""
    def colebrook_white(f):
        return 1/np.sqrt(f) + 2 * np.log10((epsilon / diam) / 3.7 + 2.51 / (re * np.sqrt(f)))
    # Solve for f using fsolve
    friction_factor: object = round(fsolve(colebrook_white, initial_guess)[0], 4)
    return friction_factor