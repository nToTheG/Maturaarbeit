#!/usr/bin/env python3

"""
"""

from __future__ import annotations
import sys
import os
import subprocess
import pathlib
import venv

ROOT = pathlib.Path(__file__).parent.resolve()
VENV_DIR = ROOT / ".venv"
REQ_FILE = ROOT / "requirements.txt"

def fail(msg: str, code: int = 1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)

def run(cmd: list[str]):
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        fail(f"Command failed: {' '.join(cmd)} (exit {e.returncode})")

def get_venv_python(p: pathlib.Path) -> pathlib.Path:
    if os.name == "nt":
        return p / "Scripts" / "python.exe"
    return p / "bin" / "python"

def main():
    # Safety checks
    if not REQ_FILE.exists():
        fail("requirements.txt not found in the same directory as this script.")
    if os.name != "nt":
        try:
            if os.geteuid() == 0:
                print("WARNING: running as root. Not recommended.", file=sys.stderr)
        except AttributeError:
            pass

    # Create venv if needed
    if VENV_DIR.exists():
        print(f"{VENV_DIR} already exists. Skipping creation.")
    else:
        print(f"Creating virtual environment at {VENV_DIR} ...")
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(str(VENV_DIR))

    venv_python = get_venv_python(VENV_DIR)
    if not venv_python.exists():
        fail(f"Could not find Python in venv at {venv_python}")

    # Upgrade pip inside venv then install requirements using venv's Python
    print("Upgrading pip inside the virtual environment...")
    run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])

    print("Installing requirements from requirements.txt ...")
    run([str(venv_python), "-m", "pip", "install", "-r", str(REQ_FILE)])

    # Usage hints
    print("\nSuccess.")
    if os.name == "nt":
        print(r"To activate (PowerShell): .\.venv\Scripts\Activate.ps1")
        print(r"To activate (cmd.exe):     .\.venv\Scripts\activate.bat")
    else:
        print("To activate (bash/zsh):    source .venv/bin/activate")

if __name__ == "__main__":
    main()
