from bitstring import BitArray, BitStream
from enum import Enum
from .util import util
from .target import Target

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
        util.debug('Vertice.__init__(algo,%s,%s,%s)', type, input_index, [predecessor.id for predecessor in predecessors] if predecessors != None else None)
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
        elif type == VerticeType.OPERATION:
            self.id = algorithm.get_operation_id()
            if predecessors == None or len(predecessors) == 0:
                util.warning('Creation of operation vertice {0} without predecessors', self.id)
                self.predecessors.append(None)
                self.predecessors.append(None)
            else:
                self.set_predecessors(predecessors)
        elif type == VerticeType.OUTPUT:
            self.id = algorithm.get_output_id()
            if predecessors == None or len(predecessors) == 0:
                self.predecessors.append(None)
            elif len(predecessors) == 1:
                self.set_predecessors(predecessors)
            else:
                util.error('Creation of output vertice {0} with more than 1 predecessor', self.id)
        util.debug(' id=%s', self.id)
        self.recompute_level()
        util.debug(' level=%s', self.level)
        self.compute_input_mask()
        util.debug(' input_mask=%s', self.get_input_mask())

    def set_predecessors(self, predecessors):
        """
        Parameters:
        - predecessors: an *exhaustive* and *sorted* list of predecessors
        """
        util.debug('%s.set_predecessors(%s)', self.id, [predecessor.id for predecessor in predecessors] if predecessors != None else None)
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

    def compute_input_mask(self):
        util.debug('%s.compute_input_mask()', self.id)
        if self.type == VerticeType.INPUT:
            self.input_mask[self.input_index] = 1
        else:
            for predecessor in self.predecessors:
                if predecessor != None:
                    self.input_mask = self.input_mask | predecessor.get_input_mask()
        util.debug('  input_mask=%s', self.input_mask)

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
        util.debug('%s.recompute_level()', self.id)
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
        util.debug(' level=%s', self.level)

    def increment_version(self):
        self.version += 1
        self.algorithm.increment_version()

    def set_execution_value(self, input_value, output_value):
        """Stores in memory an input/result pair.
        
        We apply an AND operation with the input mask, 
        like this only the input bits that are significant for this vertice are taken into account.

        Args:
            input (BitArray, string): The algorithm input. If received as string, will be converted back to BitArray.
            value (Boolean): The resulting value of this vertice for the given input.

        Returns:
            Nothing.
        """
        util.debug('%s.set_execution_value(%s, %s)', self.id, input_value, output_value)
        input_masked_key_string = self.get_input_masked_key_string(input_value)
        self.execution_values[input_masked_key_string] = output_value

    def get_input_masked_key_string(self, input_value):
        util.debug('%s.get_input_masked_key(%s)', self.id, input_value)
        input_value_as_bitarray = None
        if isinstance(input_value, BitArray):
            input_value_as_bitarray = input_value
        elif isinstance(input_value, str):
            input_value_as_bitarray = util.key_string_2_bitarray(input_value)
        else:
            util.error(' input_value: UNSUPPORTED TYPE')
        input_masked_key_string = util.bitarray_2_key_string(input_value_as_bitarray & self.input_mask)
        util.debug(' input_masked_key_string=%s', input_masked_key_string)
        return input_masked_key_string

    def get_execution_value(self, input_value):
        """Retrieve from memory the result of an input.
        
        We apply an AND operation with the input mask, 
        like this only the input bits that are significant for this vertice are taken into account.

        Args:
            input (BitArray or string): The algorithm input.

        Returns:
            Boolean value of the result or None if no execution value was found.
        """
        util.debug('%s.get_execution_value(%s)', self.id, input_value)
        execution_value = None
        input_masked_key_string = self.get_input_masked_key_string(input_value)
        if input_masked_key_string in self.execution_values.keys():
            execution_value = self.execution_values[input_masked_key_string]
        else:
            util.warning('   input_value_as_key_string: NOT IN self.execution_values.keys()')
        util.debug(' execution_value=%s', execution_value)
        return execution_value

    def get_execution_values_as_pretty_string(self):
        """
        """
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

    def set_target_value(self, input, value_as_boolean):
        """
        input: the input key string or the original BitArray
        """
        key = None
        if isinstance(input, BitArray):
            key = util.bitarray_2_key_string(input)
        elif isinstance(input, str):
            key = input
        else:
            util.error('Parameter "input" unsupported type. Value: %s', input)
        self.target_values[key] = value_as_boolean


    def get_target_value(self, input):
        """
        input: the input key string or the original BitArray
        """
        key = None
        if isinstance(input, BitArray):
            key = util.bitarray_2_key_string(input)
        elif isinstance(input, str):
            key = input
        else:
            util.error('Parameter "input" unsupported type. Value: %s', input)
        return self.target_values[key]

    def get_target_values_as_pretty_string(self):
        pretty_string = ''
        for key, value in self.target_values.items():
            pretty_string += key + '=' + util.boolean_2_pretty_string(value) + ','
        return pretty_string

    def compute_input_resulting_value(self, input_value):
        """Compute the resulting value of this input vertice for a given input parameter."""
        input_as_bitarray = None
        if isinstance(input_value, BitArray):
            input_as_bitarray = input_value
        elif isinstance(input_value, str):
            input_as_bitarray = util.key_string_2_bitarray(input_value)
        else:
            util.error('    Parameter "input" unsupported type. Value: %s', input_value)
        resulting_value = input_as_bitarray[self.input_index]
        util.debug('%s.compute_input_resulting_value(%s)=%s', self.id, input_value, resulting_value)
        self.set_execution_value(input_as_bitarray, resulting_value)

    def compute_operation_resulting_value(self, input_value):
        """Compute the resulting value of this operation vertice for a given input parameter.

        Retrieve the operation input parameters from the vertice predecessors,
        then perform (or compute) the operation on these parameters,
        finally store the resulting value (or output) in the execution value cache.
        The execution value cache is a dictionary 
        whose keys is a binary string representation of the input parameters,
        but, because only significant bits may have an effect on the resulting value,
        we apply the input mask to that key. 
        This optimization significantly reduce the number of entries in the
        execution value cache for all vertices that are not dependent 
        on all the algorithm input bits.

        Args:
            key (BitArray (preferred) or string): The algorithm input. If provided as string, will be converted to BitArray.

        Returns:
            Boolean value of the result or None if no execution value could be computed.
        """
        # TODO: check that this vertice is of type OPERATION
        # TODO: make it possible to dynamically assign a different function than NAND here
        util.debug('%s.compute_operation_resulting_value(input_value=%s)', self.id, input_value)
        input_as_bitarray = None
        resulting_value = None
        if isinstance(input_value, BitArray):
            input_as_bitarray = input_value
        elif isinstance(input_value, str):
            input_as_bitarray = util.key_string_2_bitarray(input_value)
        else:
            util.error('    Parameter "input" unsupported type. Value: %s', input_value)
        if (self.predecessors == None
            or len(self.predecessors) != 2
            or self.predecessors[0] == None 
            or self.predecessors[1] == None):
            util.warning('  Trying to compute operation without adequate predecessors. Will return None. Operation: %s', self)
            resulting_value = None
        else:
            input0 = self.predecessors[0].get_execution_value(input_as_bitarray)
            input1 = self.predecessors[1].get_execution_value(input_as_bitarray)
            if input0 == None or input1 == None:
                util.warning('  Trying to compute operation but predecessors are unable to provide execution value. Will return None. Operation: %s', self)
                resulting_value = None
            else:
                # Perform a NAND operation
                resulting_value = not (input0 and input1)
        self.set_execution_value(input_as_bitarray, resulting_value)
        util.debug('    resulting_value=%s', resulting_value)
        return resulting_value

    def compute_output_resulting_value(self, input_value):
        # TODO: check that this vertice is of type OUTPUT
        resulting_value = None
        if input_value == None:
            util.error('%s.compute_output_resulting_value(input_value=%s): input_value == None', self.id, input_value)
        if self.predecessors[0] == None:
            util.warning('%s.compute_output_resulting_value(%s)=%s: output vertice has no predecessor', self.id, input_value, None)
            resulting_value = None
        else:
            resulting_value = self.predecessors[0].get_execution_value(input_value)
        self.set_execution_value(input_value, resulting_value)
        util.debug('%s.compute_output_resulting_value(%s)=%s', self.id, input_value, resulting_value)
        return resulting_value

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

    def __str__(self):
        string_output = self.id
        string_output += ' ('
        if not self.orphaned_from_predecessors:
            string_output += ' pre:' + ','.join([predecessor.id for predecessor in self.predecessors])
        string_output += ' suc:' + ','.join([successor.id for successor in self.successors])
        string_output += ' msk:' + util.bitarray_2_key_string(self.input_mask)
        string_output += ' val:' + ''.join([util.boolean_2_pretty_string(execution_value) for execution_value in self.execution_values])
        string_output += ' tgt:' + ','.join([target_value for target_value in self.target_values])
        string_output += ' )'
        return string_output

    def __repr__(self):
        return str(self)

class VerticeType(Enum):
    INPUT = 1
    OPERATION = 2
    OUTPUT = 3

class VerticeUselessReason(Enum):
    DUPLICATE_VERTICE_WITH_IDENTICAL_PREDECESSORS = 1