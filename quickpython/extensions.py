import builtins


def beep():
    print("\a", end="")
    
    
builtins.beep = beep
