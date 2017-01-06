from Algorithm import Algorithm, Vertice, VerticeType
from bitstring import BitArray, BitStream

algo = Algorithm(4,3)

algo.define_target(BitArray('0b0000'),BitArray('0b000'))
algo.define_target(BitArray('0b0001'),BitArray('0b001'))
algo.define_target(BitArray('0b0010'),BitArray('0b010'))
algo.define_target(BitArray('0b0011'),BitArray('0b011'))
algo.define_target(BitArray('0b0100'),BitArray('0b001'))
algo.define_target(BitArray('0b0101'),BitArray('0b010'))
algo.define_target(BitArray('0b0110'),BitArray('0b011'))
algo.define_target(BitArray('0b0111'),BitArray('0b100'))
algo.define_target(BitArray('0b1000'),BitArray('0b010'))
algo.define_target(BitArray('0b1001'),BitArray('0b011'))
algo.define_target(BitArray('0b1010'),BitArray('0b100'))
algo.define_target(BitArray('0b1011'),BitArray('0b101'))
algo.define_target(BitArray('0b1100'),BitArray('0b011'))
algo.define_target(BitArray('0b1101'),BitArray('0b100'))
algo.define_target(BitArray('0b1110'),BitArray('0b110'))
algo.define_target(BitArray('0b1111'),BitArray('0b111'))

algo.search_algorithm_randomly(32000)

algo.view_as_svg()

for level in algo.operations_by_level.values():
    for operation in level:
        print(operation.id + str(': ') + str(operation.get_execution_values_as_pretty_string()))

for output in algo.outputs:
    print(output.id + ': ' + output.get_target_values_as_pretty_string())
