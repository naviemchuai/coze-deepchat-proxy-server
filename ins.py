import subprocess
import sys

def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError as e:
        return str(e)

with open('requirements.txt') as f:
    lines = f.readlines()

installable = []
uninstallable = {}

for line in lines:
    package = line.strip()
    result = install(package)
    if result is True:
        installable.append(package)
    else:
        uninstallable[package] = result

print("Installable packages:")
for package in installable:
    print(package)

print("\nUninstallable packages:")
for package, error in uninstallable.items():
    print(f"{package}: {error}")