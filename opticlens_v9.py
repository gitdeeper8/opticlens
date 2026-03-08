#!/data/data/com.termux/files/usr/bin/python
"""
OPTICLENS v9.0 - Rational-Envelope Modal Model (Fixed)
"""

import math
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# -------------------------------------------------------------------
# 1. Rational Envelope Base
# -------------------------------------------------------------------

@dataclass
class RationalEnvelope:
    """Rational (Padé-like) approximation for smooth envelope"""
    
    def __init__(self):
        self.a1_0 = 0.75
        self.a2_0 = 0.18
        self.b1_0 = 0.55
        self.b2_0 = 0.045
        
    def coefficients(self, n: float) -> Tuple[float, float, float, float]:
        dn = n - 1.5
        a1 = self.a1_0 * (1.0 + 0.3 * dn)
        a2 = self.a2_0 * (1.0 + 0.2 * dn)
        b1 = self.b1_0 * (1.0 + 0.1 * dn)
        b2 = self.b2_0 * (1.0 - 0.05 * dn)
        return a1, a2, b1, b2
    
    def compute(self, x: float, n: float) -> float:
        a1, a2, b1, b2 = self.coefficients(n)
        numerator = a1 * x * x + a2 * x
        denominator = 1.0 + b1 * x + b2 * x * x
        return 2.0 + numerator / denominator


# -------------------------------------------------------------------
# 2. Modal Oscillations
# -------------------------------------------------------------------

@dataclass
class TrainedMode:
    A_base: float
    dA_dn: float
    omega: float
    phi_base: float
    dphi_dn: float
    p: float
    
    def amplitude(self, n: float) -> float:
        return self.A_base * (1.0 + self.dA_dn * (n - 1.5))
    
    def phase(self, n: float) -> float:
        return self.phi_base + self.dphi_dn * (n - 1.5)


class ModalOscillations:
    def __init__(self):
        self.modes = [
            TrainedMode(0.82, 0.35, 2.0, -0.28, 0.15, 0.48),
            TrainedMode(0.31, 0.25, 4.0, 0.52, 0.12, 0.98),
            TrainedMode(0.14, 0.18, 6.0, 1.18, 0.08, 1.52),
            TrainedMode(0.07, 0.12, 8.0, -0.75, -0.05, 2.05),
            TrainedMode(0.04, 0.08, 10.0, 0.32, 0.03, 2.5),
            TrainedMode(0.02, 0.05, 12.0, -1.1, -0.02, 3.0),
        ]
    
    def compute(self, x: float, n: float) -> float:
        total = 0.0
        for mode in self.modes:
            A = mode.amplitude(n)
            phi = mode.phase(n)
            if x > 0:
                contrib = A * math.sin(mode.omega * x + phi) / (x ** mode.p)
            else:
                contrib = 0
            total += contrib
        return total


# -------------------------------------------------------------------
# 3. Exact Rayleigh Limit
# -------------------------------------------------------------------

def rayleigh_exact(x: float, n: float, k: float = 0.0) -> float:
    """Exact Rayleigh scattering theory"""
    m = complex(n, k)
    m2 = m * m
    alpha = (m2 - 1) / (m2 + 2)
    Q_sca = (8.0/3.0) * abs(alpha)**2 * x**4
    Q_abs = 4.0 * alpha.imag * x
    return Q_sca + Q_abs


# -------------------------------------------------------------------
# 4. Geometric Limit
# -------------------------------------------------------------------

def geometric_limit(x: float, n: float, k: float = 0.0) -> float:
    """Geometric optics limit with diffraction"""
    Q = 2.0
    if x > 10:
        Q += (4.0 / x) * math.sin(2.0 * x - math.pi/4)
    if k > 0:
        Q_abs = 1.0 - math.exp(-4.0 * k * x)
        Q += Q_abs
    return Q


# -------------------------------------------------------------------
# 5. Main Model Class (Fixed)
# -------------------------------------------------------------------

class MieRationalModalV9:
    """OPTICLENS v9.0 - Fixed version"""
    
    def __init__(self, refractive_index: complex = 1.5+0.001j):
        self.m = refractive_index
        self.n = refractive_index.real
        self.k = refractive_index.imag
        
        self.envelope = RationalEnvelope()
        self.oscillations = ModalOscillations()
        
        self.x_rayleigh = 0.1
        self.x_geometric = 100.0
    
    def size_parameter(self, wavelength: float, radius: float) -> float:
        return 2.0 * math.pi * radius / wavelength
    
    def compute(self, wavelength: float, radius: float) -> Dict:
        x = self.size_parameter(wavelength, radius)
        
        # Initialize Q_abs with default value
        Q_abs = 0.0
        
        # Rayleigh regime
        if x < self.x_rayleigh:
            Q_ext = rayleigh_exact(x, self.n, self.k)
            Q_abs = Q_ext - (8.0/3.0) * ((self.n**2-1)/(self.n**2+2))**2 * x**4
            regime = "Rayleigh"
        
        # Geometric regime
        elif x > self.x_geometric:
            Q_ext = geometric_limit(x, self.n, self.k)
            if self.k > 0:
                Q_abs = 1.0 - math.exp(-4.0 * self.k * x)
            regime = "Geometric"
        
        # Mie regime
        else:
            # Smooth envelope
            Q_base = self.envelope.compute(x, self.n)
            
            # Oscillations
            Q_osc = self.oscillations.compute(x, self.n)
            
            # Absorption
            if self.k > 0:
                Q_abs_small = 4.0 * self.k * x
                Q_abs_large = 1.0 - math.exp(-4.0 * self.k * x)
                w = math.exp(-x/10.0)
                Q_abs = w * Q_abs_small + (1 - w) * Q_abs_large
            else:
                Q_abs = 0.0
            
            # Total extinction
            Q_ext = Q_base + Q_osc + Q_abs
            
            # Regime classification
            if x < 1.0:
                regime = "Transition"
            elif x < 10.0:
                regime = "Resonance"
            else:
                regime = "Mie"
        
        # Scattering efficiency (ensure non-negative)
        Q_sca = max(0.0, Q_ext - Q_abs)
        
        # Asymmetry parameter
        if x < 0.1:
            g = 0.0
        elif x > 100:
            g = 1.0 - 1.0/x
        else:
            g = 0.5 * math.tanh((x - 3.0)/4.0) + 0.5
            g += 0.03 * (self.n - 1.5)
            g = max(0.0, min(0.95, g))
        
        # Cross sections
        area = math.pi * radius * radius
        C_ext = Q_ext * area
        C_sca = Q_sca * area
        C_abs = Q_abs * area
        
        return {
            'x': x,
            'regime': regime,
            'Q_ext': Q_ext,
            'Q_sca': Q_sca,
            'Q_abs': Q_abs,
            'g': g,
            'C_ext': C_ext,
            'C_sca': C_sca,
            'C_abs': C_abs,
            'wavelength': wavelength,
            'radius': radius,
            'n': self.n,
            'k': self.k,
        }


# -------------------------------------------------------------------
# 6. Validation
# -------------------------------------------------------------------

class ValidationV9:
    def __init__(self):
        self.ref_x = [0.1, 0.2, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 7.0, 
                     10.0, 15.0, 20.0, 30.0, 50.0, 100.0]
        self.ref_Q = [0.093, 0.320, 0.780, 2.650, 3.050, 3.210, 3.100,
                     2.980, 2.920, 2.880, 2.650, 2.420, 2.250, 2.150, 2.100]
    
    def test_bohren_huffman(self):
        print("\n📊 Bohren & Huffman (1983) Validation:")
        print("-" * 70)
        print(f"{'x':>8} {'Q_ref':>8} {'Q_v9':>8} {'Error%':>8} {'Env':>8} {'Osc':>8} {'Regime':>12}")
        print("-" * 70)
        
        model = MieRationalModalV9(refractive_index=1.5+0.001j)
        errors = []
        
        for x, q_ref in zip(self.ref_x, self.ref_Q):
            radius = x * 0.55 / (2*math.pi)
            results = model.compute(0.55, radius)
            q_v9 = results['Q_ext']
            
            # Component breakdown
            env = model.envelope.compute(x, 1.5)
            osc = model.oscillations.compute(x, 1.5)
            
            error = abs(q_v9 - q_ref) / q_ref * 100
            errors.append(error)
            
            print(f"{x:8.2f} {q_ref:8.3f} {q_v9:8.3f} {error:7.2f}% "
                  f"{env:8.3f} {osc:8.3f} {results['regime']:>12}")
        
        print("-" * 70)
        print(f"Average Error: {sum(errors)/len(errors):.2f}%")
        print(f"Max Error: {max(errors):.2f}%")
    
    def test_absorption(self):
        print("\n📊 Absorption Test (x=5.0):")
        print("-" * 60)
        print(f"{'k':>8} {'Q_ext':>10} {'Q_sca':>10} {'Q_abs':>10} {'g':>8}")
        print("-" * 60)
        
        x = 5.0
        radius = x * 0.55 / (2*math.pi)
        
        for k in [0.0, 0.001, 0.01, 0.1, 0.5]:
            model = MieRationalModalV9(refractive_index=complex(1.5, k))
            results = model.compute(0.55, radius)
            print(f"{k:8.3f} {results['Q_ext']:10.4f} "
                  f"{results['Q_sca']:10.4f} {results['Q_abs']:10.4f} {results['g']:8.3f}")


# -------------------------------------------------------------------
# 7. Main
# -------------------------------------------------------------------

def main():
    print("="*80)
    print("🔭 OPTICLENS v9.0 - Rational-Envelope Modal Model (Fixed)")
    print("="*80)
    
    validation = ValidationV9()
    validation.test_bohren_huffman()
    validation.test_absorption()
    
    print("\n" + "="*80)
    print("✅ OPTICLENS v9.0 ready!")
    print("="*80)


if __name__ == "__main__":
    main()
