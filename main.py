#!/usr/bin/env python3
"""
List installed and orphaned packages in the current Python environment.
Uses python3 -m pip to avoid PATH issues.
"""

import subprocess
import json

def get_installed_packages():
    """Get all installed packages with pip as a dict: {name: version}"""
    result = subprocess.run(
        ["python3", "-m", "pip", "list", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )
    packages = json.loads(result.stdout)
    return {pkg["name"]: pkg["version"] for pkg in packages}

def get_dependency_tree():
    """Get the pipdeptree output as JSON"""
    result = subprocess.run(
        ["python3", "-m", "pipdeptree", "--json"],
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(result.stdout)

def find_orphans():
    installed_packages = get_installed_packages()
    tree = get_dependency_tree()

    required_packages = set()
    for pkg in tree:
        for dep in pkg.get("dependencies", []):
            required_packages.add(dep["package_name"])

    orphans = [pkg for pkg in installed_packages if pkg not in required_packages]
    return orphans, installed_packages

def uninstall_package(pkg_name):
    """Uninstall a single package using python3 -m pip"""
    print(f"\nUninstalling {pkg_name}...")
    subprocess.run(["python3", "-m", "pip", "uninstall", pkg_name, "-y"])

if __name__ == "__main__":
    print("Scanning installed packages...")
    orphans, installed_packages = find_orphans()

    print("\nInstalled packages:")
    for pkg, version in installed_packages.items():
        print(f" - {pkg} ({version})")

    if not orphans:
        print("\nNo orphaned packages found.")
    else:
        print("\nOrphaned packages (not required by any other package):")
        for pkg in orphans:
            print(f" - {pkg} ({installed_packages[pkg]})")

        choice = input("\nDo you want to uninstall any of these packages? (y/n): ").strip().lower()
        if choice != "y":
            print("No packages were uninstalled.")
            exit()

        print("\nChoose an option:")
        print("1. Uninstall all orphaned packages")
        print("2. Uninstall specific package(s)")
        option = input("Enter 1 or 2: ").strip()

        if option == "1":
            for pkg in orphans:
                confirm = input(f"Do you want to uninstall {pkg} ({installed_packages[pkg]})? (y/n): ").strip().lower()
                if confirm == "y":
                    uninstall_package(pkg)
            print("\nFinished uninstalling selected orphaned packages.")

        elif option == "2":
            while True:
                pkg_input = input("Enter package name(s) to uninstall (comma separated), or 'q' to quit: ").strip()
                if pkg_input.lower() == "q":
                    break

                selected = [p.strip() for p in pkg_input.split(",") if p.strip() in orphans]
                if not selected:
                    print("No valid packages selected. Try again.")
                    continue

                for pkg in selected:
                    confirm = input(f"Do you want to uninstall {pkg} ({installed_packages[pkg]})? (y/n): ").strip().lower()
                    if confirm == "y":
                        uninstall_package(pkg)

                more = input("\nDo you want to uninstall more packages? (y/n): ").strip().lower()
                if more != "y":
                    break

        else:
            print("Invalid option. Exiting.")
