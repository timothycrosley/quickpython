import builtins
import platform
from subprocess import run


def beep():
    """Makes a beep sound."""
    print("\a", end="")


def cls():
    """Clears the screen."""
    if platform.system().lower() == "windows":
        run("cls")
    else:
        run("clear")


def main(function):
    """A decorator that causes the decorated function to be started
    if ran directly but not if imported.
    """
    caller = inspect.stack()[1]
    module = inspect.getmodule(caller[0])
    if module.__name__ == "__main__":
        function()
    return function


setattr(builtins, "beep", beep)
setattr(builtins, "cls", cls)
setattr(builtins, "main", main)
