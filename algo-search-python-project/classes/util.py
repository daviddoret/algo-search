from logging import getLogger, Formatter, StreamHandler, DEBUG, INFO, WARNING, ERROR, CRITICAL, NOTSET
from bitstring import BitArray, BitStream

# REMOVE: def get_util():
# REMOVE:     if util == None:
# REMOVE:         util = Util()
# REMOVE:     return util

class Util(object):
    """Miscelaneous Utilities"""

    def __init__(self):
        self.logger = getLogger()
        self.logger.setLevel(WARNING)
        # Console redirection
        self.__logger_stream_handler = StreamHandler()
        self.__logger_stream_handler.setLevel(WARNING)
        self.logger.addHandler(self.__logger_stream_handler)

    def set_logging_level(self, level):
        self.logger.setLevel(level)
        self.__logger_stream_handler.setLevel(level)

    def boolean_2_pretty_string(self, boolean_value):
        if boolean_value == None:
            return '.'
        elif boolean_value:
            return '1'
        else:
            return '0'

    def bitarray_2_key_string(self, bitarray):
        """
        Returns a binary string representation of the BitArray.
        """
        return (bitarray.bin)

    def key_string_2_bitarray(self, key_string):
        return BitArray(bin = key_string)

util = Util()
