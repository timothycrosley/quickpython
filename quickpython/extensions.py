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


def main(function):
    caller = inspect.stack()[1]
    module = inspect.getmodule(caller[0])
    if module.__name__ == "__main__":
        function()
    return function


setattr(builtins, "beep", beep)
setattr(builtins, "cls", cls)
setattr(builtins, "main", main)
