from bitstring import BitArray

class Target(object):
    
    def __init__(self, algorithm, input_as_bitarray, output_as_bitarray):
        self.algorithm = algorithm
        self.input = input_as_bitarray
        self.output = output_as_bitarray

    def get_key(self):
        return str(self.input)