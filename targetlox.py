import os
import sys

from lox.main import main


def entry_point(argv):
    return main(argv)


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
