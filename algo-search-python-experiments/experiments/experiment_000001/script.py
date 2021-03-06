from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from bitstring import BitArray, BitStream
from classes.algorithm import Algorithm
from classes.vertice import Vertice, VerticeType
from classes.util import util

util.set_logging_level(ERROR, logger_debug_function_depth=7)

experiment_folder = 'C:\\18-DEV\\algo-search-solution\\algo-search-python-experiments\\experiments\\experiment_000001'

algo = Algorithm(2,2)

algo.define_target(BitArray('0b00'),BitArray('0b00'))
algo.define_target(BitArray('0b01'),BitArray('0b01'))
algo.define_target(BitArray('0b10'),BitArray('0b01'))
algo.define_target(BitArray('0b11'),BitArray('0b10'))

algo.search_algorithm_randomly(256 + 128)

algo.view_as_svg()
algo.export_as_svg(filename = 'graph.svg', folder = experiment_folder)
algo.export_as_png(filename = 'graph.png', folder = experiment_folder)

for level in algo.operations_by_level.values():
    for operation in level:
        print(operation.id + str(': ') + str(operation.get_execution_values_as_pretty_string()))

for output in algo.outputs:
    print(output.id + ': ' + output.get_target_values_as_pretty_string())

#print(algo.execute(BitArray(