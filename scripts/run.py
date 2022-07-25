# -*- coding: utf-8 -*-
"""
@create: 2022-05-27 03:14:21.

@author: name

@desc: build
"""
import subprocess
import sys


def check():
    """check_code."""
    print("check_code")
    proc = subprocess.Popen("poetry run pre-commit run --all-files", shell=True)
    proc.wait()


def build():
    """build."""
    print("build")
    if sys.platform == "win32":
        proc = subprocess.Popen(".\\scripts\\build.bat", shell=True)
    else:
        proc = subprocess.Popen("chmod +x ./scripts/build.sh", shell=True)
        proc = subprocess.Popen("sh ./scripts/build.sh", shell=True)
    proc.wait()
