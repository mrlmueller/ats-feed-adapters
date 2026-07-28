"""CLI-Einstieg: python -m ats_adapters <karriere-url> [...]"""
import sys

from .ats_detect import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
