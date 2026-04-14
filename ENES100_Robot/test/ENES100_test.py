from enes100 import Enes100
import time

Enes100.begin("Material Madness", "MATERIAL", 10, 1120)

while (Enes100.isConnected()):
    print(Enes100.getX())
    time.sleep_ms(500)