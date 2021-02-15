from pyparsing import Keyword, Word, alphanums


class ConditionOperand(object):
    check_condition_fn = None

    def __init__(self, t):
        self.label = t[0]

        assert self.check_condition_fn is not None, 'The check_condition_fn should should be set'
        assert callable(self.check_condition_fn), 'The check_condition_fn should should be callable'

        self.value = self.check_condition_fn(t[0])

    def __bool__(self):
        return self.value

    def __str__(self):
        return self.label

    __repr__ = __str__
    __nonzero__ = __bool__


class BoolBinOp(object):
    def __init__(self, t):
        self.args = t[0][0::2]

    def __str__(self):
        sep = " %s " % self.reprsymbol
        return "(" + sep.join(map(str, self.args)) + ")"

    def __bool__(self):
        return self.evalop(bool(a) for a in self.args)

    __nonzero__ = __bool__
    __repr__ = __str__


class BoolAnd(BoolBinOp):
    reprsymbol = '&'
    evalop = all


class BoolOr(BoolBinOp):
    reprsymbol = '|'
    evalop = any


class BoolNot(object):
    def __init__(self, t):
        self.arg = t[0][1]

    def __bool__(self):
        v = bool(self.arg)
        return not v

    def __str__(self):
        return "~" + str(self.arg)

    __repr__ = __str__
    __nonzero__ = __bool__


TRUE = Keyword("True")
FALSE = Keyword("False")
boolOperand = TRUE | FALSE | Word(alphanums + '_:.*', max=256)
