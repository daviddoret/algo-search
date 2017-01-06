from enum import Enum
from Target import Target
from Util import util

class Vertice(object):
    """
    This is not a strict vertice as per graph theory, 
    it is a Binary Algorithm Vertice
    """

    def __init__(self
                 , algorithm
                 , type
                 , input_index = None
                 , predecessors = None):
        self.version = 1
        self.algorithm = algorithm
        self.predecessors = []
        self.orphaned_from_predecessors = True # Initialized as orphaned and this will change as soon as precessors are set.
        self.successors = []
        self.type = type
        self.execution_values = {}
        self.target_values = {}
        self.level = None
        self.input_index = input_index
        self.input_mask = self.algorithm.get_empty_input_mask()
        self.useless = False # Until proved otherwise, vertices are assumed to play a useful role in the algorithm.
        if type == VerticeType.INPUT:
            self.id = algorithm.get_input_id()
            # Configure the input mask.
            self.input_mask[input_index] = 1
        elif type == VerticeType.OPERATION:
            self.id = algorithm.get_operation_id()
            if predecessors == None or len(predecessors) == 0:
                util.logger.warning('Creation of operation vertice {0} without predecessors', self.id)
                self.predecessors.append(None)
                self.predecessors.append(None)
            else:
                self.set_predecessors(predecessors)
            # REMOVE: initializes the predecessors. since these are "mandatory",
            # REMOVE: it is simpler to let the user know the positions in the list
            # REMOVE: have been pre-initialized and may be accessed directly by
            # REMOVE: index position.
            # REMOVE: for position in range(0, predecessors_number):
            # REMOVE:    self.predecessors.append(None)
            # REMOVE: for predecessor_index in range(0,len(predecessors)):
            # REMOVE:    if not self.set_predecessor(predecessors[predecessor_index], predecessor_index):
            # REMOVE:        XXX
        elif type == VerticeType.OUTPUT:
            self.id = algorithm.get_output_id()
            if predecessors == None or len(predecessors) == 0:
                self.predecessors.append(None)
            elif len(predecessors) == 1:
                self.set_predecessors(predecessors)
            else:
                util.logger.error('Creation of output vertice {0} with more than 1 predecessor', self.id)
        self.recompute_level()

    def set_predecessors(self, predecessors):
        """
        Parameters:
        - predecessors: an *exhaustive* and *sorted* list of predecessors
        """
        if predecessors == None:
            self.orphaned_from_predecessors = True
            self.predecessors = []
        elif len(predecessors) == 0:
            self.orphaned_from_predecessors = True
            self.predecessors = []
        elif(self.algorithm.request_operation_by_predecessors_index_authorization(
            operation = self
            ,candidate_predecessors = predecessors)):
            self.orphaned_from_predecessors = False
            self.predecessors = list(predecessors)
            self.compute_input_mask()
            self.recompute_level()
            for predecessor in predecessors:
                predecessor.append_successor(self)
        else:
            self.orphaned_from_predecessors = True
            self.useless = True
            self.useless_reason = VerticeUselessReason.DUPLICATE_VERTICE_WITH_IDENTICAL_PREDECESSORS

    # REMOVE: def set_predecessor(self, predecessor, index):
    # REMOVE:     """
    # REMOVE:     Returns: True|False (if the predecessor was successfuly configured)
    # REMOVE:     """
    # REMOVE:     if self.algorithm.request_operation_by_predecessors_index_authorization(self):
    # REMOVE:         #TODO: if successor predecessor was already configured, 
    # REMOVE:         #   remove first the corresponding edge
    # REMOVE:         self.predecessors[index] = predecessor
    # REMOVE:         self.recompute_level()
    # REMOVE:         return True
    # REMOVE:     else:
    # REMOVE:         # This configuration has not been authorized because
    # REMOVE:         # it would create a duplicate operation (i.e. two
    # REMOVE:         # operations with the same predecessors.
    # REMOVE:         return False

    def compute_input_mask(self):
        for predecessor in self.predecessors:
            self.input_mask = self.input_mask | predecessor.get_input_mask()

    def get_input_mask(self):
        return self.input_mask

    def reset_executions(self):
        """
        called by Algorithm.reset_executions()
        """
        self.execution_values = {}

    def recompute_level(self):
        #possible improvement: this is not efficient and may lead to multiple
        #   useless duplicate recomputations that in voluminous graphs could
        #   lead to decreased performances. if this becomes an issue, there is
        #   room for optimization here.
        new_level = None
        if self.type == VerticeType.INPUT:
            new_level = 1
        else:
            for predecessor in self.predecessors:
                if predecessor != None and predecessor.level != None:
                    if new_level == None:
                        new_level = predecessor.level + 1
                    else:
                        new_level = max(new_level, predecessor.level + 1)
        if new_level != self.level:
            self.level = new_level
            if(self.algorithm.max_level == None):
                self.algorithm.max_level = new_level
            elif new_level != None:
                self.algorithm.max_level = max(self.algorithm.max_level, new_level)
            for successor in self.successors:
                successor.recompute_level()
            self.increment_version()

    def increment_version(self):
        self.version += 1
        self.algorithm.increment_version()

    def set_execution_value(self, input_as_bitarray, value):
        """
        We apply an AND operation with the input mask, 
        like this only the input bits that are significant for this vertice are taken into account.
        """
        self.execution_values[util.bitarray_2_key_string(input_as_bitarray & self.input_mask)] = value

    def get_execution_value(self, input_as_bitarray):
        if util.bitarray_2_key_string(input_as_bitarray) in self.execution_values:
            return self.execution_values[util.bitarray_2_key_string(input_as_bitarray)]
        else:
            return None

    def get_execution_values_as_pretty_string(self):
        if self.execution_values == None:
            return 'None'
        elif len(self.execution_values) == 0:
            return 'Empty'
        else:
            pretty_string = ''
            for key, value in self.execution_values.items():
                if key == None:
                    pretty_string += 'None'
                else:
                    pretty_string += key
                pretty_string += '=' + util.boolean_2_pretty_string(value) + ','
            return pretty_string

    def set_target_value(self, input_as_bitarray, value_as_boolean):
        self.target_values[util.bitarray_2_key_string(input_as_bitarray)] = value_as_boolean

    def get_target_value(self, input_as_bitarray):
        return self.target_values[util.bitarray_2_key_string(input_as_bitarray)]

    def get_target_values_as_pretty_string(self):
        pretty_string = ''
        for key, value in self.target_values.items():
            pretty_string += key + '=' + util.boolean_2_pretty_string(value) + ','
        return pretty_string

    def compute_operation(self, key):
        # TODO: check that this vertice is of type OPERATION
        # TODO: make it possible to dynamically assign a different function than NAND here
        input0 = self.predecessors[0].get_execution_value(key)
        input1 = self.predecessors[1].get_execution_value(key)
        output_value = not (input0 and input1)
        self.set_execution_value(key, output_value)
        return output_value

    def retrieve_output(self, key):
        # TODO: check that this vertice is of type OUTPUT
        if self.predecessors[0] == None:
            output_value = None
        else:
            output_value = self.predecessors[0].get_execution_value(key)
        self.set_execution_value(key, output_value)
        return output_value

    def append_successor(self, successor):
        """
        Inputs and Operations can have any number of successors.
        """
        self.successors.append(successor)

    # REMOVE: def get_predecessors_index_keys(self):
    # REMOVE:     """
    # REMOVE:     The key used to maintain the Algorithm.operations_by_predecessors_index index.
    # REMOVE:     Making it possible to prevent the creation of duplicate Operations.
    # REMOVE: 
    # REMOVE:     LIMITATION: We only support 2 predecessors here. If we want to work
    # REMOVE:         with other operations than NAND that takes higher number of predecessors,
    # REMOVE:         we will need to review this method and return all combinations.
    # REMOVE:     """
    # REMOVE:     if self.predecessors[0] != None and self.predecessors[1] != None:
    # REMOVE:         # All predecessors have been configured,
    # REMOVE:         # we can now provide a correct index key.
    # REMOVE:         return list(
    # REMOVE:             self.predecessors[0].id + '-' + self.predecessors[1].id,
    # REMOVE:             self.predecessors[1].id + '-' + self.predecessors[0].id)
    # REMOVE:     else:
    # REMOVE:         return None

class VerticeType(Enum):
    INPUT = 1
    OPERATION = 2
    OUTPUT = 3

class VerticeUselessReason(Enum):
    DUPLICATE_VERTICE_WITH_IDENTICAL_PREDECESSORS = 1