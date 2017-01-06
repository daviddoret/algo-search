from logging import getLogger, Formatter, StreamHandler, DEBUG
from bitstring import BitArray, BitStream

# REMOVE: def get_util():
# REMOVE:     if util == None:
# REMOVE:         util = Util()
# REMOVE:     return util

class Util(object):
    """Miscelaneous Utilities"""

    def __init__(self):
        self.logger = getLogger()
        self.logger.setLevel(DEBUG)
        # Console redirection
        steam_handler = StreamHandler()
        steam_handler.setLevel(DEBUG)
        self.logger.addHandler(steam_handler)

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

util = Util()
