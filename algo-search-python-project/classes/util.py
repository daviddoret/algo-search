from logging import getLogger, Formatter, StreamHandler, DEBUG, INFO, WARNING, ERROR, CRITICAL, NOTSET
from bitstring import BitArray, BitStream
from inspect import getouterframes, currentframe
import os
import sys

# REMOVE: def get_util():
# REMOVE:     if util == None:
# REMOVE:         util = Util()
# REMOVE:     return util

class AlgoSearchException(Exception):
    """Exceptions raised by the Algo-Search project"""

class Util(object):
    """Miscelaneous Utilities"""

    def __init__(self):
        self.__logger = getLogger()
        self.__logger.setLevel(WARNING)
        # Console redirection
        self.__logger_stream_handler = StreamHandler()
        self.__logger_stream_handler.setLevel(WARNING)
        formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.__logger_stream_handler.setFormatter(formatter)
        self.__logger.addHandler(self.__logger_stream_handler)
        self.__logger_debug_function_depth = 12

    def set_logging_level(self, level, logger_debug_function_depth = 7):
        self.__logger_debug_function_depth = logger_debug_function_depth
        self.__logger.setLevel(level)
        self.__logger_stream_handler.setLevel(level)

    def debug(self, msg, *args, **kwargs):
        level = len(getouterframes(currentframe())) - 1 #Remove 1 for the call to util.debug()
        if level <= self.__logger_debug_function_depth:
            msg = ' ' * level + msg
            self.__logger.debug(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        level = len(getouterframes(currentframe())) - 1 #Remove 1 for the call to util.debug()
        msg = ' ' * level + msg
        self.__logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        level = len(getouterframes(currentframe())) - 1 #Remove 1 for the call to util.debug()
        msg = ' ' * level + msg
        self.__logger.error(msg, *args, **kwargs)
        raise AlgoSearchException(msg, *args, **kwargs)

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

    def ternary_operator(self, condition, value_if_true, value_if_false):
        if condition:
            return value_if_true
        else:
            return value_if_false

util = Util()
