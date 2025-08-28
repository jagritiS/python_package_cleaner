# Python Package Cleaner

### A simple Python script to:

1. List all installed packages with version and usage.

2. Classify packages as:

    System (do not remove)

    Required by another package

    Application (safe to uninstall if unused)

3. Detect and display orphaned packages (installed but not required by others).

4. Provide an interactive uninstall tool for orphaned packages.

5. Automatically installs pipdeptree if missing.

# Features
### Shows packages in a nice table with a header as 
- Package, Version, Used By

1. Interactive uninstall options:

2. Remove all orphaned packages

3. Remove specific orphaned packages

Helps keep your Python environment clean and lightweight.

# Installation

Clone the repository and install dependencies:

git clone https://github.com/<your-username>/python-package-cleaner.git
cd python-package-cleaner
python3 python_package_cleaner.py


If you don’t have pipdeptree, don’t worry — the script will install it automatically.

# Usage

Run the script:

python python_package_cleaner.py

Example output:
Scanning installed packages...
Table of all the installed packages 
Then the script will ask:

Orphaned packages safe to uninstall:
 - openai (1.102.0)
 - pandas (2.3.2)

Do you want to uninstall any of these packages? (y/n):

System packages (pip, setuptools, wheel, etc.) are marked as do not remove.

Removing required packages may break dependencies.

# Contributing

## PRs are welcome! Feel free to fork this repo, improve the script, and submit pull requests.

# License

MIT License.
