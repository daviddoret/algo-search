class Execution(object):
    """State information of an algorithm execution"""

    def __init__(self, algorithm, input):
        self.execution = None
        self.algorithm = algorithm
        self.input = input  
        self.output = None
        self.key = self.generate_key()

    def generate_key(self):
        """
        In an older version, I used a version/input pair like this:
            self.key = 'v' + str(self.algorithm.version) + 'i' + str(self.input)
        Like this, the execution cache could support multiple versions of the algorithm.
        But re-thinking this, I don't see much added value in maintaining execution
        cache for older versions of the algorithm and I fear this will consume a lot
        of memory when working on random searches.
        So finally, I decided to simplify the execution cache and reset it to free
        memory whenever we recompile the algorithm.
        """
        return str(self.input)
