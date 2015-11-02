__author__ = 'Roger'


class Node(object):
    def __init__(self, toks=None):
        if toks:
            self.val = toks[0]
            self.repr = str(toks[0])
        else:
            self.val = None
            self.repr = ''

    def eval(self, env=None):
        pass

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.repr

    def __eq__(self, other):
        try:
            return self.__dict__ == other.__dict__
        except AttributeError:
            return False


class DecEval(Node):
    def __init__(self, toks):
        """ :rtype : str, hash, self
            :param toks:
        """
        super(DecEval, self).__init__()
        self.val = int(toks[0])

    def __str__(self):
        return str(self.val)

    def __hash__(self):
        return hash(self.val)

    def eval(self, env=None):
        return self

        # def __add__(self, other):
        #     if isinstance(other, floatEval):
        #         return other + self
        #     try:
        #         return DecEval([str(self.val + other.val)])
        #     except AttributeError:
        #         return DecEval([str(self.val + other)])
        #
        # def __neg__(self):
        #     out = copy.deepcopy(self)
        #     out.val  = -out.val
        #     return out
        #
        # def __abs__(self):
        #     if self.val < 0:
        #         return -self
        #     return copy.deepcopy(self)
        #
        # def __mod__(self, other):
        #     try:
        #         return DecEval([str(self.val % other.val)])
        #     except AttributeError:
        #         return DecEval([str(self.val % other)])
        # def __pow__(self, other):
        #     try:
        #         return DecEval([str(self.val ** other.val)])
        #     except AttributeError:
        #         return DecEval([str(self.val ** other)])
        #
        # def _convert(self, other):
        #     if hasattr(other, 'val'):
        #         return other
        #     elif isinstance(other, float):
        #         return floatEval([str(other).upper()])
        #     return DecEval([str(other).upper()])
        #
        # def __mul__(self,other):
        #     if isinstance(other, floatEval):
        #         return other * self
        #     other = self._convert(other)
        #     return DecEval([str(self.val*other.val)])
        # def __radd__(self, other):
        #     return self.__add__(other)
        # def __rmul__(self,other):
        #     return self.__mul__(other)
        #
        # def __div__(self,other):
        #     if isinstance(other, floatEval):
        #         return other.__rdiv__(self)
        #     other = self._convert(other)
        #     try:
        #         return DecEval([str(self.val/other.val)])
        #     except ZeroDivisionError:
        #         print 'Warning!!: division by zero!!!'
        #         return DecEval(['0'])
        #
        # def __rdiv__(self,other):
        #     try:
        #         return DecEval([str(other/self.val).upper()])
        #     except ZeroDivisionError:
        #         print 'Warning!!: division by zero!!!'
        #         return DecEval(['0'])
        # def __sub__(self,other):
        #     if isinstance(other, floatEval):
        #         return (-other) + self
        #     other = self._convert(other)
        #     return DecEval([str(self.val - other.val)])
        # def __lshift__(self,other):
        #     other = self._convert(other)
        #     return DecEval([str(self.val << other.val)])
        # def __rshift__(self,other):
        #     other = self._convert(other)
        #     return DecEval([str(self.val >> other.val)])
        # def __or__(self,other):
        #     other = self._convert(other)
        #     return DecEval([str(self.val | other.val)])
        # def __and__(self,other):
        #     other = self._convert(other)
        #     return DecEval([str(self.val & other.val)])
        # def __xor__(self,other):
        #     other = self._convert(other)
        #     return DecEval([str(self.val ^ other.val)])
        # def __invert__(self):
        #     return DecEval([str(~self.val)])
        # def __cmp__(self,other):
        #     try:
        #         return cmp(self.val, other.val)
        #     except AttributeError:
        #         return cmp(self.val, other)
        # def __nonzero__(self):
        #     return self.val !=0


class hexEval(DecEval):
    def __init__(self, toks):
        super(hexEval, self).__init__(toks)
        self.val = int(toks[0], 16)
        self.repr = str(self.val)
