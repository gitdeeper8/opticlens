#!/usr/bin/env python3

"""OPTICLENS v10.0.0 Upload - Historical Release"""

import requests
import hashlib
import os
import glob
import sys

# قم بتعيين التوكن كمتغير بيئة أو استبدله هنا
TOKEN = os.environ.get('PYPI_TOKEN', '')

if not TOKEN:
    print("❌ خطأ: لم يتم تعيين PYPI_TOKEN")
    print("   قم بتعيين التوكن كمتغير بيئة:")
    print("   export PYPI_TOKEN='pypi-xxxxxx'")
    sys.exit(1)

print("="*70)
print("🔭 OPTICLENS v10.0.0 Upload - PyPI")
print("   🏆 First Python package with 0% error in Mie scattering")
print("   DOI: 10.5281/zenodo.18907508")
print("="*70)

# قراءة README.md
with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()
print(f"\n📄 README.md: {len(readme)} حرف")

# البحث عن ملفات التوزيع
wheel_files = glob.glob("dist/*.whl")
tar_files = glob.glob("dist/*.tar.gz")

if not wheel_files and not tar_files:
    print("\n📦 لا توجد ملفات توزيع. جاري بناء الحزمة...")
    os.system("python -m build")
    wheel_files = glob.glob("dist/*.whl")
    tar_files = glob.glob("dist/*.tar.gz")

print(f"\n📦 الملفات المكتشفة:")
for f in wheel_files + tar_files:
    size = os.path.getsize(f) / 1024
    print(f"   • {os.path.basename(f)} ({size:.1f} KB)")

# رفع كل ملف
success_count = 0
for filepath in wheel_files + tar_files:
    filename = os.path.basename(filepath)
    print(f"\n📤 رفع: {filename}")

    with open(filepath, 'rb') as f:
        content = f.read()
    md5_hash = hashlib.md5(content).hexdigest()
    sha256_hash = hashlib.sha256(content).hexdigest()

    filetype = 'sdist' if filename.endswith('.tar.gz') else 'bdist_wheel'
    pyversion = 'source' if filename.endswith('.tar.gz') else 'py3'

    data = {
        ':action': 'file_upload',
        'metadata_version': '2.1',
        'name': 'opticlens',
        'version': '10.0.0',
        'filetype': filetype,
        'pyversion': pyversion,
        'md5_digest': md5_hash,
        'sha256_digest': sha256_hash,
        'description': readme,
        'description_content_type': 'text/markdown',
        'author': 'Samir Baladi',
        'author_email': 'gitdeeper@gmail.com',
        'license': 'CC BY 4.0',
        'summary': 'OPTICLENS: Optical Phenomena, Turbulence & Imaging — Light Environmental Nonlinearity System',
        'home_page': 'https://opticlens.netlify.app',
        'requires_python': '>=3.8',
    }

    with open(filepath, 'rb') as f:
        response = requests.post(
            'https://upload.pypi.org/legacy/',
            files={'content': (filename, f, 'application/octet-stream')},
            data=data,
            auth=('__token__', TOKEN),
            timeout=120,
        )

    print(f"   الحالة: {response.status_code}")

    if response.status_code == 200:
        print("   ✅✅✅ نجاح!")
        success_count += 1
    else:
        print(f"   ❌ خطأ: {response.text[:200]}")

print("\n" + "="*70)
print(f"📊 ملخص الرفع: {success_count}/{len(wheel_files + tar_files)} ملفات نجحت")

if success_count > 0:
    print("\n✅✅✅ تم رفع OPTICLENS v10.0.0 بنجاح!")
    print("\n🔗 https://pypi.org/project/opticlens/")
    print("   https://doi.org/10.5281/zenodo.18907508")
else:
    print("\n❌❌❌ فشل الرفع!")

print("="*70)
