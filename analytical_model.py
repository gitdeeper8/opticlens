#!/data/data/com.termux/files/usr/bin/python
"""
نموذج تحليلي مبسط لـ Mie Scattering
يعمل بدون مكتبات خارجية
"""

import math

def mie_rayleigh(x, m):
    """نموذج رايلي للجسيمات الصغيرة (x << 1)"""
    m_sq = m*m
    term = (m_sq - 1) / (m_sq + 2)
    Q_scat = (8/3) * x**4 * abs(term)**2
    return Q_scat

def mie_geometric(x):
    """نموذج هندسي للجسيمات الكبيرة (x >> 1)"""
    return 2.0

def analytical_mie(wavelength, radius, refractive_index):
    """
    نموذج تحليلي يجمع بين رايلي والهندسي
    """
    x = 2 * math.pi * radius / wavelength
    
    if x < 0.1:
        Q = mie_rayleigh(x, refractive_index)
        regime = "Rayleigh"
    elif x > 100:
        Q = mie_geometric(x)
        regime = "Geometric"
    else:
        # نظام انتقالي - متوسط مرجح
        w_ray = max(0, 1 - math.log10(x/0.1))
        w_geo = 1 - w_ray
        Q_ray = mie_rayleigh(x, refractive_index)
        Q_geo = mie_geometric(x)
        Q = w_ray * Q_ray + w_geo * Q_geo
        regime = "Transition"
    
    return Q, regime, x

def run_tests():
    """تشغيل الاختبارات"""
    print("🔭 OPTICLENS - Analytical Model Tests")
    print("="*50)
    
    # قيم الاختبار من ملفات tests
    test_cases = [
        {"name": "Rayleigh Test", "wavelength": 0.55, "radius": 0.001, "m": 1.5, "expected": "Rayleigh"},
        {"name": "Mie Test", "wavelength": 0.55, "radius": 0.1, "m": 1.5, "expected": "Transition"},
        {"name": "Geometric Test", "wavelength": 0.55, "radius": 100, "m": 1.5, "expected": "Geometric"},
    ]
    
    for test in test_cases:
        print(f"\n🧪 {test['name']}:")
        Q, regime, x = analytical_mie(test['wavelength'], test['radius'], test['m'])
        print(f"  size parameter x = {x:.4f}")
        print(f"  regime = {regime}")
        print(f"  Q_ext = {Q:.6f}")
        
        if regime == test['expected']:
            print(f"  ✅ PASS: Expected {test['expected']}")
        else:
            print(f"  ❌ FAIL: Expected {test['expected']}, got {regime}")
    
    print("\n" + "="*50)
    print("✅ Tests completed!")

if __name__ == "__main__":
    run_tests()
