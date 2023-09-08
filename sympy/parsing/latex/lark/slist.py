from sympy import AtomicExpr, Add, Mul, Pow, Expr


class SList(list):
    def __new__(cls, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], Expr):
            return cls.from_sympy(args[0])
        return list.__new__(cls)

    @staticmethod
    def from_sympy(expr):
        if isinstance(expr, AtomicExpr):
            return expr
        return SList([type(expr)] + [SList.from_sympy(arg) for arg in expr.args])

    def build(self, evaluate: bool = True):
        return self[0](*[arg.build(evaluate) if isinstance(arg, SList) else arg for arg in self[1:]], evaluate=evaluate)

    def __repr__(self):
        return repr(self.build(evaluate=False))

    def __str__(self):
        return str(self.build(evaluate=False))

    def __add__(self, other):
        return SList([Add, self, other])

    def __sub__(self, other):
        return SList([Add, self, SList([Mul, -1, other])])

    def __mul__(self, other):
        return SList([Mul, self, other])

    def __truediv__(self, other):
        return SList([Mul, self, SList([Pow, other, -1])])

    def __pow__(self, power, modulo=None):
        return SList([Pow, self, power])
