from enum import Enum
from graphviz import Digraph
from bitstring import BitArray, BitStream
import timeit
#import secret
import random
from .vertice import Vertice, VerticeType
from .execution import Execution
from .target import Target
from .util import util

class Algorithm(object):
    """A binary algorithm modeled as an acyclic directed graph"""

    def __init__(self, input_size, output_size, title=None):
        self.version = 1
        self.compiled_version = None
        self.last_input_id = -1
        self.last_operation_id = -1
        self.last_output_id = -1
        self.vertices = []
        self.input_size = input_size
        self.inputs = []
        self.operations = []
        self.operations_by_level = None # To facilitate the analysis of operations level by level in ascending/descending order
        self.operations_by_predecessors_index = {} # To prevent the creation of duplicate operations
        self.output_size = output_size
        self.outputs = []
        self.max_level = None # directly kept up-to-date by the vertices
        self.initialize_input(input_size)
        self.initialize_output(output_size)
        self.executions = {}
        self.targets = {}
        self.title = title

    def initialize_input(self, size_in_bits):
        """creates the input vertices for a given size of binary input"""
        # first, remove any existing input vertices
        for vertice in self.inputs:
            self.remove_vertice(vertice)
        for index in range(0,size_in_bits):
            vertice = Vertice(self, VerticeType.INPUT, input_index = index)
            self.add_vertice(vertice)

    def initialize_output(self, size_in_bits):
        """creates the output vertices for a given size of binary output"""
        # first, remove any existing output vertices
        for vertice in self.outputs:
            self.remove_vertice(vertice)
        for number in range(0,size_in_bits):
            vertice = Vertice(self, VerticeType.OUTPUT, predecessors = None)
            self.add_vertice(vertice)

    def get_empty_input_mask(self):
        """
        Returns a bit mask of size equivalent to the number of inputs.
        Used to initialize the input bit mask of vertices.
        """
        return BitArray(length=self.input_size)

    def request_operation_by_predecessors_index_authorization(self, operation, candidate_predecessors):
        """
        """
        util.debug('algo.request_operation_by_predecessors_index_authorization(operation=%s, candidate_predecessors=%s)', operation.id, ','.join(predecessor.id for predecessor in candidate_predecessors))
        if candidate_predecessors == None:
            return True
        elif len(candidate_predecessors) == 0:
            return True
        else:
            candidate_predecessors_ids = [vertice.id for vertice in candidate_predecessors]
            candidate_predecessors_ids_sorted = sorted(candidate_predecessors_ids)
            key_as_string = ','.join(candidate_predecessors_ids_sorted)
            util.debug('    key_as_string=%s', key_as_string)
            if key_as_string in self.operations_by_predecessors_index:
                util.debug('    return=False')
                return False
            else:
                self.operations_by_predecessors_index[key_as_string] = operation
                util.debug('    return=True')
                return True

    def create_operation(self, predecessors):
        """
        """
        util.debug('algo.create_operation(%s)', [predecessor.id for predecessor in predecessors] if predecessors != None else None)
        if(predecessors == None):
            util.error(' predecessors==None',)
        elif(len(predecessors) != 2):
            # For the time being, we do not support other functions than NAND
            # thus I strictly test for 2 predecessors.
            util.error(' len(predecessors)!=2')
        operation = Vertice(self, VerticeType.OPERATION, predecessors = predecessors)
        self.add_vertice(operation)
        util.debug(' return=%s',operation.id)
        return operation

    def create_random_operation(self): #, max_random_predecessor_selection_attempts=4):
        
        # TODO: use better PRG with the secrets lib
        #   unfortunately, the secrets lib failed to install

        # OPTIMIZATION: picking up all random predecessors is wrong because
        #   when one predecessor has been "used" a lot, making 8 attempts
        #   will probably not be enough to go find the other candidate predecessors.
        #   Instead, we should pick randomely the first predecessor and then
        #   PICK RANDOMLY AMONGST THE REMAINING POSSIBLE VERTICES THE SECOND
        #   PREDECESSOR.

        # OPTIMIZATION: here, I assume we create many many duplicate operations.
        #   the first optimization should be that no two vertices may have the
        #   same predecessors. and because the NAND operation does not make a difference
        #   on the predecessor position, this rule should not be dependent on the 
        #   position of the predecessors.

        # OPTIMIZATION: check NAND execution pathes that lead to equivalent
        #   results. Then, mark these as useless and remove them from any further effort.
        util.debug('algo.create_random_operation()')

        possibilities = len(self.inputs) + len(self.operations)
        #random_predecessor_selection_attempts = 1
        random_operation = None

        #while random_predecessor_selection_attempts < max_random_predecessor_selection_attempts:
        predecessors = []
        keep_trying = True
        while keep_trying:
            random_number = random.randint(1,possibilities)
            if random_number <= len(self.inputs):
                # the random predecessor will be an input
                predecessor = self.inputs[random_number - 1]
                # REMOVE: predecessors.append(self.inputs[random_number - 1])
            else:
                predecessor = self.operations[random_number - len(self.inputs) - 1]
                # REMOVE: predecessors.append(self.operations[random_number - len(self.inputs) - 1])
            if not predecessor.useless:
                keep_trying = False
                predecessors.append(predecessor)
        keep_trying = True
        while keep_trying:
            random_number = random.randint(1,possibilities)
            if random_number <= len(self.inputs):
                # the random predecessor will be an input
                predecessor = self.inputs[random_number - 1]
                # REMOVE: predecessors.append(self.inputs[random_number - 1])
            else:
                predecessor = self.operations[random_number - len(self.inputs) - 1]
                # REMOVE: predecessors.append(self.operations[random_number - len(self.inputs) - 1])
            if not predecessor.useless:
                keep_trying = False
                predecessors.append(predecessor)

        random_operation = self.create_operation(predecessors)
        if random_operation.useless:
            util.warning(' random_operation.useless=%s',random_operation.useless)
            #random_operation = None # To prevent returning a useless operation
            #random_predecessor_selection_attempts += 1
        #else:
        #    exit
        util.debug(' random_operation=%s',random_operation.id if random_operation != None else None)
        return random_operation
            
    def search_algorithm_randomly(self, max_iterations=1024):
        util.debug('algo.search_algorithm_randomly(max_iterations=%s)',max_iterations)
        # TODO: REVIEW THE METHOD PARAMETERS, THEY NEED BE RENAMED AND REVIEWED, 
        #   e.g. we no longer use batches.
            
        # assumption: target_values have been defined with define_target() first

        # Executes the algorithm once for every target input.
        # This will initialize the inputs, etc.
        # Of course, because the algorithm does not have any operation yet,
        # these executions will run very fast and yield nothing.
        #self.execute_all_target_inputs()

        for input in self.inputs:
            self.compute_single_input_over_all_targets(input)

        for output in self.outputs:
            util.debug('    %s.target_values=%s', output.id, output.get_target_values_as_pretty_string())

        # makes a copy of the output list
        output_searched = list(self.outputs)

        # continue iterating the search until all outputs have been succesfuly mapped
        iteration = 1

        while len(output_searched) > 0 and iteration <= max_iterations:
            util.debug('    iteration=%s',iteration)
            iteration += 1

            random_operation = self.create_random_operation()
            
            if random_operation == None:
                util.warning('  random_operation==None')
            else:
                util.debug('    random_operation=%s',random_operation.id)
                self.compute_single_operation_over_all_targets(random_operation)
                util.debug('    random_operation.execution_values=%s',random_operation.get_execution_values_as_pretty_string())

                for output in output_searched:

                    match = True

                    for input_key_string in output.target_values.keys():
                        if output.get_target_value(input_key_string) != random_operation.get_execution_value(input_key_string):
                            match = False
                            break
                    util.debug('    output.id=%s',output.id)
                    util.debug('    output.target_values=%s',output.get_target_values_as_pretty_string())
                    util.debug('    match=%s',match)
                    if match:
                        # This operation matches the target value requirements of this output
                        # Remove this output from the list of outputs being searched
                        output_searched.remove(output)
                        # And link this operation with this output
                        output.set_predecessors([random_operation])
                        # ASSUMPTIONS: There are no 2 outputs with identical targets,
                        #   otherwise we would miss the second one.
                        break

        # TODO: output some metrics (% output success, etc.)

        # OPTIMIZATION: if operation is not useless

        # LATER: optimize the algorithm by marking vertices that are
        #   dead-ends because useless and ensure these are excluded
        #   from the create_random_operation() method

        # LATER: make it possible to save algos in files and load from files

        # LATER: make it possible to pretty print an algo
        #   possible generate an image and find a cool graph library for that
        #   installed python graphviz package + graphviz for windows,
        #   let's test this.

        # SECONDARY OPTIMIZATION IDEA: if two outputs have the
        # same vertical target values, don't do the work twice.

    def define_target(self, input_value, output_value):
        """will typically be called multiple times to populate the target values
        that will be used to automatically infer the algorithm"""
        util.debug('algo.define_target(input_value=%s, output_value=%s)',input_value, output_value)
        target = Target(self, input_value, output_value)
        self.targets[util.bitarray_2_key_string(input_value)] = target
        # synchronize the target_values of the algo outputs
        # to facilitate vertical (truth table) comparison
        for output_index in range(0, len(self.outputs)):
            self.outputs[output_index].set_target_value(target.input, output_value[output_index])        

    def add_vertice(self, vertice):
        """safe method to add new vertices to the graph
        guarantees consistency of internal lists"""
        self.vertices.append(vertice)
        if(vertice.type == VerticeType.INPUT):
            self.inputs.append(vertice)
        elif(vertice.type == VerticeType.OPERATION):
            self.operations.append(vertice)
        elif(vertice.type == VerticeType.OUTPUT):
            self.outputs.append(vertice)
        self.increment_version()

    def get_input_id(self):
        self.last_input_id += 1
        return 'i' + str(self.last_input_id)

    def get_operation_id(self):
        self.last_operation_id += 1
        return 'p' + str(self.last_operation_id)

    def get_output_id(self):
        self.last_output_id += 1
        return 'o' + str(self.last_output_id)

    def remove_vertice(self, vertice):
        """safe method to remove a vertice from a graph
        guarantees consistency of internal lists"""
        self.vertices.remove(vertice)
        if(vertice.type == VerticeType.INPUT):
            self.inputs.remove(vertice)
        elif(vertice.type == VerticeType.OPERATION):
            self.operations.remove(vertice)
        elif(vertice.type == VerticeType.OUTPUT):
            self.outputs.remove(vertice)
        #TODO: remove all linked edges
        self.increment_version()

    # REMOVE: def set_edge(self, predecessor, successor, index):
    # REMOVE:     """
    # REMOVE:     Returns: True|False (depending if the configuration was successful or not)
    # REMOVE:     """
    # REMOVE:     if successor.set_predecessor(predecessor, index):
    # REMOVE:         #the successor has strictly positioned predecessors
    # REMOVE:         #the predecessor can have any number of successors
    # REMOVE:         predecessor.append_successor(successor)
    # REMOVE:         self.increment_version()
    # REMOVE:         return True
    # REMOVE:     else:
    # REMOVE:         # This edge was refused, most probably because
    # REMOVE:         # it would create a duplicate operation.
    # REMOVE:         return False

    #def remove_edge(self, predecessor, successor, successor_position):
        #TO BE COMPLETED

    def increment_version(self):
        self.version += 1

    def compile(self):
        """to speed execution, populates the per level collections of operations"""
        self.reset_executions()
        self.recompute_level()
        self.compiled_version = self.version

    def recompute_level(self):
        """
        Ensures that the level of all vertices is up-to-date.
        Ensures that every vertice is properly allocated to its by-level collection.
        """
        for input in self.inputs:
            input.recompute_level() 
            # this triggers level recomputation for successor vertices

        self.operations_by_level = {}

        # for each operation level, initialize a list
        # self.max_level = output level, but range() does not generate the stop value
        for level in range(2, self.max_level + 1):
            self.operations_by_level[level] = []
        
        # assign every operation vertice to its level list
        for vertice in self.operations:
            if vertice.level != None:
                self.operations_by_level[vertice.level].append(vertice)

    def reset_executions(self):
        """
        Clear the execution cache.
        The execution cache comprises:
        - Algorithm.executions
        - Vertice.execution_values
        """
        self.executions = {}
        for vertice in self.vertices:
            vertice.reset_executions()

    def execute_all_target_inputs(self):
        """
        Execute the complete algorithm for every target inputs.
        This is typically used at the beginning of an algorithm search to initialize inputs, etc.
        """
        for target in self.targets.values():
            self.execute(target.input)

    def compute_single_input_over_all_targets(self, input_vertice):
        # OPTIMIZATION: Execute only the distinct inputs after application of the input mask.
        for target in self.targets.values():
            input_vertice.compute_input_resulting_value(target.input)

    def compute_single_operation_over_all_targets(self, operation_vertice):
        """
        On a single operation vertice, executes the operation for all target inputs.
        This is typically used as part of an algorithm search process.
        """
        # OPTIMIZATION: Execute only the distinct inputs after application of the input mask.
        util.debug('algo.compute_single_operation_over_all_targets(%s)', operation_vertice.id if operation_vertice != None else None)
        if operation_vertice == None:
            util.error('    operation_vertice=None')
        for target in self.targets.values():
            operation_vertice.compute_operation_resulting_value(target.input)

    def execute(self, input_as_bitarray):
        """
        Execute the complete algorithm with one particular input and returns the output.
        input: an input in BitArray format to perform the execution on that input value only.
        """

        # compilation if needed
        if self.version != self.compiled_version:
            self.compile()

        # initialization
        execution = Execution(self, input_as_bitarray)
        self.executions[execution.key] = execution

        # start performance timer
        execution_start = timeit.default_timer()

        # set the values of all inputs
        for input_bit_position in range(0,len(input_as_bitarray)):
            self.inputs[input_bit_position].compute_input_resulting_value(input_as_bitarray)
            #self.inputs[input_bit_position].set_execution_value(execution.key, input_as_bitarray[input_bit_position])

        # loop through operations from level 2 to n
        # self.max_level = output level, but range() does not generate the stop value
        for level in range(2, self.max_level):
            for operation in self.operations_by_level[level]:
                operation.compute_operation_resulting_value(input_as_bitarray)

        # set the values of all outputs
        output_as_bitarray = BitArray(length = len(self.outputs))
        for output_index in range(0, len(self.outputs)):
            output_value = self.outputs[output_index].compute_output_resulting_value(input_as_bitarray)
            output_as_bitarray.set(output_value, output_index)
        execution.output = output_as_bitarray

        # stop performance time
        execution_end = timeit.default_timer()
        execution.time = execution_end - execution_start

        # return the output value
        return output_as_bitarray

    def get_graphviz_dot(self):

        # IMPROVEMENT: Apply different colors to useful / useless verticices
        #   This can be done by havin a Vertice.is_useful attribute.
        
        # IMPROVEMENT: Color in red the critical path of vertices that lead to an output
        #   This can be done by having a Vertice.is_on_the_critical_path attribute.

        self.recompute_level()

        main_graph = Digraph('Algorithm', format='pdf')
        input_cluster = Digraph('cluster_01')
        input_cluster.body.append('style=filled')
        input_cluster.body.append('fillcolor=lightgrey')
        input_cluster.body.append('color=lightgrey')
        input_cluster.body.append('label="Inputs"')
        operation_cluster = Digraph('cluster_02')
        operation_cluster.body.append('label="Operations"')
        operation_cluster.body.append('style=filled')
        operation_cluster.body.append('fillcolor=white')
        operation_cluster.body.append('color=lightgrey')
        output_cluster = Digraph('cluster_03')
        output_cluster.body.append('style=filled')
        output_cluster.body.append('fillcolor=lightgrey')
        output_cluster.body.append('color=lightgrey')
        output_cluster.body.append('label="Outputs"')
        for input in self.inputs:
            input_cluster.node(input.id, label=input.id, shape='rect', color='blue')
        for level in range(2, self.max_level + 1):
            level_cluster = Digraph('cluster_0' + str(level + 2))
            level_cluster.body.append('label="Level ' + str(level) + '"')
            level_cluster.body.append('style=filled')
            level_cluster.body.append('fillcolor=white')
            level_cluster.body.append('color=lightgrey')
            for operation in self.operations_by_level[level]:
                label = operation.id + ' ' + operation.get_execution_values_as_pretty_string()
                color = 'grey'
                if operation.useless:
                    color = 'red'
                level_cluster.node(operation.id, label=label, shape='rect', color=color)
            operation_cluster.subgraph(level_cluster)
        for output in self.outputs:
            label = output.id + ' ' + operation.get_target_values_as_pretty_string()
            output_cluster.node(output.id, label=output.id, shape='rect', color='green')
        main_graph.subgraph(input_cluster)
        main_graph.subgraph(operation_cluster)
        main_graph.subgraph(output_cluster)
        for vertice in self.vertices:
            for successor in vertice.successors:
                color = 'black'
                if vertice.type == VerticeType.INPUT:
                    color = 'blue'
                elif successor.type == VerticeType.OUTPUT:
                    color = 'green'
                main_graph.edge(vertice.id, successor.id, color=color) #, constraint='false')
        return main_graph

    def export_as_graphviz_dot(self):
        return print(self.get_graphviz_dot().source)

    def view_as_pdf(self):
        graph = self.get_graphviz_dot()
        graph.format = 'pdf'
        graph.view()

    def view_as_svg(self):
        graph = self.get_graphviz_dot()
        graph.format = 'svg'
        graph.view()
