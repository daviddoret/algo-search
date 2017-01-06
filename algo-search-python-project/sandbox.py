from enum import Enum
import timeit
from bitstring import BitArray, BitStream
import random

x = BitArray(length=32)
print(str(x.bin))

x[8] = 1
x[10] = True
x[9] = 0
print(str(x.bin))

y = BitArray(length=32)
y[2] = 1
y[8] = 1
print(str(y.bin))

z = x | y
print(str(z.bin))



"""
y = list()
y.append('a')
y.append('b')
y.append('c')
z = list(y)
z.remove('a')
print(z)
print(y)
"""

"""
a = BitArray('0b101010')
for bit in a:
    print(bit)
"""

"""
for i in range(1,2):
    print(i)
"""

"""
random_number = random.randint(0,4)
print (random_number)
random_number = random.randint(0,4)
print (random_number)
random_number = random.randint(0,4)
print (random_number)
random_number = random.randint(0,4)
print (random_number)
random_number = random.randint(0,4)
print (random_number)
random_number = random.randint(0,4)
print (random_number)
random_number = random.randint(0,4)
print (random_number)
random_number = random.randint(0,4)
print (random_number)
"""

