# Keep terminal window up.
import atexit

def press_to_close():
    input("Press ENTER to close.")

atexit.register(press_to_close)
