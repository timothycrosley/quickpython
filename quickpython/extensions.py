import builtins
import platform
from subprocess import run


def beep():
    print("\a", end="")


def cls():
    if platform.system().lower() == "windows":
        run("cls")
    else:
        run("clear")


builtins.beep = beep
builtins.cls = cls
