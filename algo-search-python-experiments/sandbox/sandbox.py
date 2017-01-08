from enum import Enum
import timeit
from bitstring import BitArray, BitStream
import random
from classes.target import Target

"""
a = dict()
a['a'] = 'hello'
a['b'] = 'bonjour'
print(a)
"""

y = BitArray(bin='1010')
print(y.bin)
print(y[2])
print(type(y[2]))
"""
dico = {}

dico['00'] = Target(None, BitArray(bin='001'), BitArray(bin='010'))
dico['01'] = Target(None, BitArray(bin='011'), BitArray(bin='100'))
dico['10'] = Target(None, BitArray(bin='101'), BitArray(bin='110'))
dico['11'] = Target(None, BitArray(bin='111'), BitArray(bin='000'))

mask = BitArray(bin='110')

#results = map(lambda x: x ^ mask, [o.input for o in dico.values()])

results = [o.input & mask for o in dico.values()]

for result in results:
    print(result.bin)
"""