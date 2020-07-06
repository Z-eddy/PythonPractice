import random
import sys
rVal=0
for i in range(100):
    rVal=random.randint(0,100)
    if rVal==98:
        sys.exit()

print("end")