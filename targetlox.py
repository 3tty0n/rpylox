import os
import sys

from lox.main import main


def entry_point(argv):
    return main(argv)


def target(driver, _args):
    exe_name = "rlox"

    if driver.config.translation.jit:
        exe_name += "-jit"
    else:
        exe_name += "-interp"

    driver.exe_name = exe_name
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
