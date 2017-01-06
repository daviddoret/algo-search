from enum import Enum
import timeit
from bitstring import BitArray, BitStream
import random

x = BitArray('0b11110000')
print(x.bin)
print(type(x.bin))