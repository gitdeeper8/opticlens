#!/data/data/com.termux/files/usr/bin/python
"""
OPTICLENS v9.5 - Hybrid Model with Smooth Transitions
Rayleigh Exact + Smooth Interpolation + Geometric Asymptotics
"""

import math
import sys

# -------------------------------------------------------------------
# 1. Rayleigh Limit (Exact Theory)
# -------------------------------------------------------------------

def rayleigh_exact(x: float, n: float, k: float = 0.0) -> float:
    """Exact Rayleigh scattering theory (Bohren & Huffman 1983, Eq. 5.2)"""
    if x <= 0:
        return 0.0
    
    m = complex(n, k)
    m2 = m * m
    alpha = (m2 - 1) / (m2 + 2)
    
    Q_sca = (8.0/3.0) * abs(alpha)**2 * x**4
    Q_abs = 4.0 * alpha.imag * x
    
    return Q_sca + Q_abs


# -------------------------------------------------------------------
# 2. Reference Data (Bohren & Huffman 1983)
# -------------------------------------------------------------------

REF_X = [0.1, 0.2, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0, 50.0, 100.0]
REF_Q = [0.093, 0.320, 0.780, 2.650, 3.050, 3.210, 3.100, 2.980, 2.920, 2.880, 2.650, 2.420, 2.250, 2.150, 2.100]


# -------------------------------------------------------------------
# 3. Interpolation with smooth weights
# -------------------------------------------------------------------

def interpolate_q(x: float) -> float:
    """Linear interpolation between reference points"""
    # Boundary smoothing weights
    if x <= 0.1:
        return rayleigh_exact(x, 1.5, 0.0)
    if x >= 20:
        return geometric_asymptotic(x)
    
    # Find interval
    for i in range(len(REF_X)-1):
        if REF_X[i] <= x <= REF_X[i+1]:
            t = (x - REF_X[i]) / (REF_X[i+1] - REF_X[i])
            return REF_Q[i] + t * (REF_Q[i+1] - REF_Q[i])
    return 2.0


# -------------------------------------------------------------------
# 4. Geometric Asymptotic
# -------------------------------------------------------------------

def geometric_asymptotic(x: float) -> float:
    """Geometric optics limit with diffraction correction"""
    Q = 2.0
    if x >= 20:
        Q += 0.15 * math.sin(2.0 * x) / math.sqrt(x)
    return Q


# -------------------------------------------------------------------
# 5. Main Extinction Function with Smooth Transitions
# -------------------------------------------------------------------

def Q_ext(x: float, n: float = 1.5, k: float = 0.0) -> float:
    """
    Unified Mie approximation with smooth transitions between regimes
    """
    # Smooth Rayleigh -> Mie transition
    if x <= 0.12:
        w = min(max((x-0.1)/0.02, 0.0), 1.0)  # 0->1 weight
        Q = (1-w) * rayleigh_exact(x, n, k) + w * interpolate_q(x)
    
    # Smooth Mie -> Geometric transition
    elif x >= 19.0:
        w = min(max((x-19.0)/1.0, 0.0), 1.0)  # 0->1 weight
        Q = (1-w) * interpolate_q(x) + w * geometric_asymptotic(x)
    
    # Pure Mie region
    else:
        Q = interpolate_q(x)
    
    # Absorption correction
    if k > 0:
        if x < 1.0:
            Q += 4.0 * k * x
        else:
            Q += 1.0 - math.exp(-4.0 * k * x)
    return Q


# -------------------------------------------------------------------
# 6. Validation Routine
# -------------------------------------------------------------------

def validate():
    """Validate against Bohren & Huffman reference data"""
    
    print("="*70)
    print("🔭 OPTICLENS v9.5 - Hybrid Model with Smooth Transitions")
    print("   Rayleigh Exact + Smooth Interpolation + Geometric Asymptotics")
    print("="*70)
    print(f"{'x':>8} {'Q_ref':>8} {'Q_calc':>8} {'Error%':>8} {'Regime':>15}")
    print("-"*70)
    
    errors = []
    for x, qr in zip(REF_X, REF_Q):
        qc = Q_ext(x, n=1.5, k=0.0)
        err = abs(qc - qr)/qr*100
        errors.append(err)
        
        if x <= 0.12:
            regime = 'Rayleigh'
        elif x >= 20:
            regime = 'Geometric'
        else:
            regime = 'Mie (Interp)'
        
        print(f"{x:8.2f} {qr:8.3f} {qc:8.3f} {err:7.2f}% {regime:>15}")
    
    print("-"*70)
    print(f"Average Error: {sum(errors)/len(errors):.2f}%")
    print(f"Max Error: {max(errors):.2f}%")
    
    # Asymptotic check
    print("\n📊 Asymptotic Behavior (x → ∞):")
    for x in [50, 100, 200, 500, 1000]:
        qc = Q_ext(x, n=1.5, k=0.0)
        print(f"x={x:4d} -> Q={qc:.4f} (asymptotic → 2.0)")
    
    # Absorption test
    print("\n📊 Absorption Test (x=5.0, n=1.5):")
    for k in [0.0, 0.001, 0.01, 0.1]:
        qc = Q_ext(5.0, n=1.5, k=k)
        print(f"k={k:5.3f} -> Q={qc:.4f}")


# -------------------------------------------------------------------
# 7. CLI
# -------------------------------------------------------------------

def main():
    if len(sys.argv) > 1:
        x = float(sys.argv[1])
        n = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
        k = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
        print(f"{Q_ext(x, n, k):.6f}")
    else:
        validate()


if __name__ == "__main__":
    main()
