from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
import unittest
from bitstring import BitArray, BitStream
from classes.algorithm import Algorithm
from classes.vertice import Vertice, VerticeType
from classes.util import util

util.set_logging_level(DEBUG)

class Test_Check(unittest.TestCase):

    def test_001(self):
        """Check automated testing works properly"""
        self.assertEqual(1,1)

    def test_002(self):
        self.assertEqual(BitArray('0b1010'), BitArray('0b1010'))

    def test_003(self):
        """Check the proper functioning of a simple algorithm"""
        a = Algorithm(2,1)
        self.assertEqual(len(a.inputs),2)
        self.assertEqual(len(a.outputs),1)

        version_test = a.version
        nand = a.create_operation([a.inputs[0], a.inputs[1]])
        self.assertGreater(a.version, version_test)

        version_test = a.version
        a.outputs[0].set_predecessors([nand])
        self.assertGreater(a.version, version_test)

        version_test = a.version
        self.assertEqual(a.inputs[0].level, 1)
        self.assertEqual(a.inputs[1].level, 1)
        self.assertEqual(nand.level, 2)
        self.assertEqual(a.outputs[0].level, 3)

        output = a.execute(BitArray('0b00'))
        self.assertEqual(output, BitArray('0b1'))

        output = a.execute(BitArray('0b01'))
        self.assertEqual(output, BitArray('0b1'))

        output = a.execute(BitArray('0b10'))
        self.assertEqual(output, BitArray('0b1'))

        output = a.execute(BitArray('0b11'))
        self.assertEqual(output, BitArray('0b0'))

        print(a.export_as_graphviz_dot())
        a.view_as_svg()

        print('STOP')

    #def test_003(self):
    #    self.assertEqual(1,2)

if __name__ == '__main__':
    unittest.main(exit=False)
