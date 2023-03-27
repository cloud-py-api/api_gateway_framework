"""
Simplest example.
"""

import sys
from time import sleep

if __name__ == "__main__":
    print("hello world!")
    print(f"me was run with {len(sys.argv) - 2} arguments from NC.")
    sleep(float(sys.argv[1]))
    print("exit")
    sys.exit(0)
