from bitstring import BitArray

# REMOVE: NO LONGER IN USE, FINALLY I USE DIRECTLY THE BOOLEAN VALUE IN THE DICTIONARY

class Target(object):
    
    def __init__(self, algorithm, input_as_bitarray, output_as_bitarray):
        self.algorithm = algorithm
        self.input = input_as_bitarray
        self.output = output_as_bitarray
