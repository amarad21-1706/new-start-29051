import sys
print("Python executable being used:", sys.executable)
print("Python version:", sys.version)
print("sys.path:", sys.path)

try:
    import email_validator
    print("email_validator is installed and imported successfully!")
except ModuleNotFoundError:
    print("email_validator is not found.")
