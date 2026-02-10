import os
import subprocess
import sys
import importlib


def find_python_files(directory):
    """Find all Python files in the given directory."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files


def get_imports(file_path):
    """Extract all imports from a Python file."""
    imports = set()
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('import') or line.startswith('from'):
                parts = line.split()
                if parts[0] == 'import':
                    imports.add(parts[1].split('.')[0])
                elif parts[0] == 'from':
                    imports.add(parts[1].split('.')[0])
    return imports


def check_and_install(package):
    """Check if a package is installed; if not, prompt the user to install it."""
    try:
        importlib.import_module(package)
        print(f"{package} is already installed.")
    except ImportError:
        print(f"{package} is not installed.")
        user_input = input(f"Do you want to install {package}? (y/n): ").strip().lower()
        if user_input == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def main():
    base_path = input("Enter the base path to check for dependencies: ").strip()

    if not os.path.isdir(base_path):
        print(f"The path '{base_path}' is not a valid directory.")
        return

    python_files = find_python_files(base_path)
    all_imports = set()

    for file_path in python_files:
        print(f"Checking imports in {file_path}...")
        imports = get_imports(file_path)
        all_imports.update(imports)

    for package in all_imports:
        check_and_install(package)

    print("Dependency check completed.")


if __name__ == "__main__":
    main()
