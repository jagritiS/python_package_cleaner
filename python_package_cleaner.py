#!/usr/bin/env python3
"""
List installed and orphaned packages in the current Python environment.
Shows which packages are system vs application.
Allows interactive uninstall of orphaned packages.
Automatically installs pipdeptree if missing.
"""

import subprocess
import json
import sys
import sysconfig
from pathlib import Path

def ensure_pipdeptree():
    try:
        subprocess.run(
            [sys.executable, "-m", "pipdeptree", "--version"],
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError:
        print("pipdeptree not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pipdeptree"], check=True)
        print("pipdeptree installed successfully.")

def get_installed_packages():
    """Return all installed packages with version and location"""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=json", "--verbose"],
        capture_output=True,
        text=True,
        check=True
    )
    packages = json.loads(result.stdout)
    return {
        pkg["name"]: {
            "version": pkg["version"],
            "location": pkg.get("Location", "")
        }
        for pkg in packages
    }

def get_dependency_tree():
    result = subprocess.run(
        [sys.executable, "-m", "pipdeptree", "--json"],
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(result.stdout)

def classify_packages(installed_packages):
    """Classify packages as system or application and detect orphaned ones"""
    tree = get_dependency_tree()
    required_packages = set()
    for pkg in tree:
        for dep in pkg.get("dependencies", []):
            required_packages.add(dep["package_name"])

    system_dirs = ["/Library/", "/System/", "/Applications/Xcode.app/"]
    skip_packages = {"pip", "setuptools", "wheel", "pipdeptree"}

    classified = {}
    for pkg, data in installed_packages.items():
        pkg_path = data.get("location", "")
        is_system = any(pkg_path.startswith(sd) for sd in system_dirs) or pkg in skip_packages
        used_by = "system (do not remove)" if is_system else ("application" if pkg not in required_packages else "required by another package")
        classified[pkg] = {
            "version": data["version"],
            "used_by": used_by,
            "system": is_system
        }
    return classified

def display_packages(classified):
    print(f"{'Package':<20} {'Version':<10} {'Used By'}")
    print("-" * 50)
    for pkg, info in classified.items():
        print(f"{pkg:<20} {info['version']:<10} {info['used_by']}")

def uninstall_package(pkg_name):
    """Uninstall a single package using the same Python interpreter"""
    print(f"\nUninstalling {pkg_name}...")
    subprocess.run([sys.executable, "-m", "pip", "uninstall", pkg_name, "-y"])

def interactive_uninstall(classified):
    # Only consider application packages for uninstall
    orphaned = [pkg for pkg, info in classified.items() if info["used_by"] == "application"]

    if not orphaned:
        print("\nNo orphaned packages safe to uninstall.")
        return

    print("\nOrphaned packages safe to uninstall:")
    for pkg in orphaned:
        print(f" - {pkg} ({classified[pkg]['version']})")

    choice = input("\nDo you want to uninstall any of these packages? (y/n): ").strip().lower()
    if choice != "y":
        return

    print("\nChoose an option:")
    print("1. Uninstall all orphaned packages")
    print("2. Uninstall specific package(s)")
    option = input("Enter 1 or 2: ").strip()

    if option == "1":
        for pkg in orphaned:
            confirm = input(f"Do you want to uninstall {pkg} ({classified[pkg]['version']})? (y/n): ").strip().lower()
            if confirm == "y":
                uninstall_package(pkg)
        print("\nFinished uninstalling selected orphaned packages.")

    elif option == "2":
        while True:
            pkg_input = input("Enter package name(s) to uninstall (comma separated), or 'q' to quit: ").strip()
            if pkg_input.lower() == "q":
                break

            selected = [p.strip() for p in pkg_input.split(",") if p.strip() in orphaned]
            if not selected:
                print("No valid packages selected. Try again.")
                continue

            for pkg in selected:
                confirm = input(f"Do you want to uninstall {pkg} ({classified[pkg]['version']})? (y/n): ").strip().lower()
                if confirm == "y":
                    uninstall_package(pkg)

            more = input("\nDo you want to uninstall more packages? (y/n): ").strip().lower()
            if more != "y":
                break
    else:
        print("Invalid option. Exiting.")

if __name__ == "__main__":
    ensure_pipdeptree()
    print("Scanning installed packages...")
    installed_packages = get_installed_packages()
    classified = classify_packages(installed_packages)
    display_packages(classified)
    interactive_uninstall(classified)
