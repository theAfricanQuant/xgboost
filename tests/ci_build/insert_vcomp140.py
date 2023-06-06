import sys
import re
import zipfile
import glob

if len(sys.argv) != 2:
    print(f'Usage: {sys.argv[0]} [wheel]')
    sys.exit(1)

vcomp140_path = 'C:\\Windows\\System32\\vcomp140.dll'

for wheel_path in sorted(glob.glob(sys.argv[1])):
    m = re.search(r'xgboost-(.*)-py3', wheel_path)
    assert m
    version = m[1]

    with zipfile.ZipFile(wheel_path, 'a') as f:
        f.write(vcomp140_path, f'xgboost-{version}.data/data/xgboost/vcomp140.dll')
