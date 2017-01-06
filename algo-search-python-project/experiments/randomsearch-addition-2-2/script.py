from Algorithm import Algorithm, Vertice, VerticeType
from bitstring import BitArray, BitStream

algo = Algorithm(2,2)

algo.define_target(BitArray('0b00'),BitArray('0b00'))
algo.define_target(BitArray('0b01'),BitArray('0b01'))
algo.define_target(BitArray('0b10'),BitArray('0b01'))
algo.define_target(BitArray('0b11'),BitArray('0b10'))

algo.search_algorithm_randomly(128)

algo.view_as_svg()

for level in algo.operations_by_level.values():
    for operation in level:
        print(operation.id + str(': ') + str(operation.get_execution_values_as_pretty_string()))

for output in algo.outputs:
    print(output.id + ': ' + output.get_target_values_as_pretty_string())

#print(algo.execute(BitArray(