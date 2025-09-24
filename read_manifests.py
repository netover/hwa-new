import os
import glob

def read_manifests():
    # Define the file patterns for each type of manifest file
    patterns = [
        "requirements*.txt",
        "package.json",
        "Cargo.toml",
        "pom.xml",
        "Gemfile"
    ]

    for pattern in patterns:
        files = glob.glob(pattern, recursive=True)
        for file in files:
            print(f"Contents of {file}:")
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    print(f.read())
                print("\n" + "="*40 + "\n")
            except FileNotFoundError:
                print(f"{file} not found.")
            except Exception as e:
                print(f"An error occurred while reading {file}: {e}")

if __name__ == "__main__":
    read_manifests()
