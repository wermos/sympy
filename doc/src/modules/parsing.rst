=======
Parsing
=======

.. module:: sympy.parsing

Parsing Functions Reference
---------------------------

.. autofunction:: sympy.parsing.sympy_parser.parse_expr

.. autofunction:: sympy.parsing.sympy_parser.stringify_expr

.. autofunction:: sympy.parsing.sympy_parser.eval_expr

.. autofunction:: sympy.parsing.maxima.parse_maxima

.. autofunction:: sympy.parsing.mathematica.parse_mathematica

Parsing Transformations Reference
---------------------------------

A transformation is a function that accepts the arguments ``tokens,
local_dict, global_dict`` and returns a list of transformed tokens. They can
be used by passing a list of functions to :py:func:`~.parse_expr` and are
applied in the order given.

.. autodata:: sympy.parsing.sympy_parser.standard_transformations

.. autofunction:: sympy.parsing.sympy_parser.split_symbols

.. autofunction:: sympy.parsing.sympy_parser.split_symbols_custom

.. autofunction:: sympy.parsing.sympy_parser.implicit_multiplication

.. autofunction:: sympy.parsing.sympy_parser.implicit_application

.. autofunction:: sympy.parsing.sympy_parser.function_exponentiation

.. autofunction:: sympy.parsing.sympy_parser.implicit_multiplication_application

.. autofunction:: sympy.parsing.sympy_parser.rationalize

.. autofunction:: sympy.parsing.sympy_parser.convert_xor

These are included in
:data:`sympy.parsing.sympy_parser.standard_transformations` and generally
don't need to be manually added by the user.

.. autofunction:: sympy.parsing.sympy_parser.lambda_notation

.. autofunction:: sympy.parsing.sympy_parser.auto_symbol

.. autofunction:: sympy.parsing.sympy_parser.repeated_decimals

.. autofunction:: sympy.parsing.sympy_parser.auto_number

.. autofunction:: sympy.parsing.sympy_parser.factorial_notation

Experimental `\mathrm{\LaTeX}` Parsing
--------------------------------------

The current implementations are experimental. The behavior, parser backend(s) and
API might change in the future. Unlike some of the other parsers, `\mathrm{\LaTeX}` is
designed as a *type-setting* language, not a *computer algebra system* and so
can contain typographical conventions that might be interpreted multiple ways.

`\mathrm{\LaTeX}` Parsing Functions Reference
---------------------------------------------

.. autofunction:: sympy.parsing.latex.parse_latex

ANTLR Backend
^^^^^^^^^^^^^

The ANTLR-based `\mathrm{\LaTeX}` parser was ported from
`latex2sympy <https://github.com/augustt198/latex2sympy>`_. While it is functional
and its API should remain stable, the parsing behavior or backend may change in
future releases.

.. _ANTLR parser caveats:

ANTLR `\mathrm{\LaTeX}` Parser Caveats
""""""""""""""""""""""""""""""""""""""

Currently, the parser may fail to fully parse an expression, but not throw a
warning::

    parse_latex(r'x -')

will simply find ``x``. What is covered by this behavior will almost certainly
change between releases, and become stricter, more relaxed, or some mix.

Lark Backend
^^^^^^^^^^^^

The Lark-based LaTeX parser is newer, and is intended to eventually completely
replace the ANTLR-based parser. It has most of the features that the ANTLR-based
parser provides, with some extras.

Lark `\mathrm{\LaTeX}` Parser Features
""""""""""""""""""""""""""""""""""""""

One thing to note is that the Lark backend does not support ill-formed expressions,
and it does not try to fix any sort of common mistakes that may have occurred. For
example, as mentioned in :ref:`the earlier section <ANTLR parser caveats>`, the
ANTLR-based parser would simply find ``x`` if we run::

    parse_latex(r'x -', backend='antlr')

However, running::

    parse_latex(r'x -', backend='lark')

will raise an ``lark.exceptions.UnexpectedEOF`` exception.

Input that does not fit the grammar raises the exceptions of Lark, like
``lark.exceptions.UnexpectedEOF`` and ``lark.exceptions.UnexpectedCharacters``.
A command that the parser does not know, like ``\mathbf`` or ``\partial``,
raises a ``LaTeXParsingError`` with a message like ``Unknown command
\mathbf`` before the input is parsed. Input that parses but cannot be turned
into an expression, like the determinant of something that is not a matrix,
also raises a ``LaTeXParsingError``.

Apart from that, there are a couple of extra things that the Lark-based parser
supports that the ANTLR-based parser does not. They are:

1. Detecting ambiguous expressions, and
2. Allowing user-customization of the `\mathrm{\LaTeX}` grammar at runtime.

Expressions like `f(x)` are technically ambiguous `\mathrm{\LaTeX}` expressions
because the `f` might be a function or a variable name. Lark has the capability to
point out these ambiguities and notify the user, or even return all possible
interpretations.

When the input is ambiguous, ``parse_latex_lark`` (and ``parse_latex`` with
``backend="lark"``) does not return a SymPy expression. It returns a
``lark.Tree`` whose ``data`` is ``"_ambig"`` and whose children are the
possible readings. For example, ::

    parse_latex_lark(r"f(x)")

gives us ::

    Tree('_ambig', [f(x), f*x])

``parse_latex_lark_all`` returns the readings as a list instead, which is
``[f(x), f*x]`` here, and a list with one element when the input is not
ambiguous.

Since any single letter followed by parentheses can be read both ways, this
also happens inside larger expressions like `\int_a^b f(x) \, dx`. Writing
the function as ``\operatorname{f}(x)`` makes it unambiguous.

The Lark-based parser exposes a number of internals which allow the user to customize
the parser's behavior. For example, the user can specify their own `\mathrm{\LaTeX}`
grammar by passing the path to the grammar file to the ``LarkLaTeXParser`` while
instantiating the parser.

The user can also specify their own custom transformer class to the ``LarkLaTeXParser``
class.

The two examples mentioned above can be found in the
`test_custom_latex.py <https://github.com/sympy/sympy/blob/395e820b114d2b169483354f1f4ee2f439faa292/sympy/parsing/tests/test_custom_latex.py>`_
file.

Lark `\mathrm{\LaTeX}` Parser Capabilities
""""""""""""""""""""""""""""""""""""""""""

In order to use the Lark-based LaTeX parser, it is important to know what it can
and cannot do. As the parser is still experimental, it supports many things, but
some features are still only partially implemented, or not available.

As such, we will list the types of expressions that it can parse, and then list
some expression types of interest where it may fail.

Here is a list of the things which are supported:

* Symbols which consist of one letter, e.g., ``a``, ``b``, ``x``, etc.
  Greek symbols and symbols with subscripts are also supported. Numbers are also
  supported, as is ``\infty``. `\pi` and `\mathrm{e}` are the constants. A
  plain ``e`` is read as a symbol, not as Euler's number.
* Symbols with multiple letters are supported, as long as they are wrapped in
  ``\mathit``.
* Expressions with `+`, `-`, `*`, `/`, and alternative operators like ``\cdot``,
  ``\times``, ``\div``, etc. If two expressions are next to each other, like `xy`
  or `(\sin x)(\cos t)`, then it is treated as implicit multiplication.
* Relations with `<`, `>`, `\le`, `\ge`, `=`, and `\ne`, including chains like
  `a < b \le c`, and membership in a number set like `x \in \mathbb{R}`.
  `\le` can also be written as ``\leq``, ``\leqslant`` or ``\leqq``, `\ge` as
  ``\geq``, ``\geqslant`` or ``\geqq``, and `\ne` as ``\neq``. A chain is read
  as the ``And`` of the relations between neighbouring terms, so `a < b \le c`
  gives ``(a < b) & (b <= c)``. The number sets are `\mathbb{N}`,
  `\mathbb{Z}`, `\mathbb{Q}`, `\mathbb{R}` and `\mathbb{C}`, and ``\notin``
  is also supported.
* Commonly used functions like

    * Square roots,
    * factorials,
    * complex conjugation (like `\overline{z}`)
    * `\log`, which is the natural logarithm unless a base is given, as in
      `\log_2 x`,
    * `\ln`,
    * `\lg`, which is the logarithm to base 10,
    * `\exp`,
    * absolute value (e.g., `|x|`). Note that `||x||` is parsed as ``Abs(Abs(x))``.
    * floor (e.g., `\lfloor x \rfloor`) and ceiling (e.g., `\lceil x \rceil`),
    * `\min` and `\max`,
    * degrees, like `x^\circ`, which are converted to radians, so `90^\circ`
      gives ``pi/2``.

* Complex numbers via the use of `\backslash \mathrm{imaginaryunit}`. For example::

    parse_latex(r"5 + 3\imaginaryunit", backend="lark")

  gives us the output of ``5 + 3*I``. A plain ``i`` is read as a symbol, and
  ``\mathrm{i}`` is not supported. ``\imaginaryunit`` is not a standard
  `\mathrm{\LaTeX}` command, so it usually has to be defined in the document,
  for example with ``\newcommand{\imaginaryunit}{i}``.
* All the trigonometric functions and their inverses trigonometric functions.
  Powers like ``\sin^4`` are also supported. The power `-1` is interpreted as the
  inverse function (i.e., ``\sin^{-1} x`` is interpreted as ``\arcsin x``).
* Hyperbolic trigonometric functions (`\sinh`, `\cosh`, `\tanh`, `\coth`,
  ``\sech`` and ``\csch``) and their inverses. The inverses of `\sinh`, `\cosh`
  and `\tanh` can be written as ``\arsinh`` or ``\arcsinh``, and so on. As
  mentioned in the previous point, powers like ``\tanh^2`` are also supported,
  and `-1` is interpreted as the inverse function (i.e., ``\tanh^{-1} x`` is
  interpreted as ``\arctanh x``). This is also the only way to write the
  inverses of `\coth`, ``\sech`` and ``\csch``.
* ``AppliedFunctions``, like `f(x, y, z)`, and functions named with
  ``\operatorname``: `\operatorname{sin} x` is the sine and
  `\operatorname{erf}(x)` the error function, while a name that is not known,
  as in `\operatorname{f}(x)`, gives an undefined function. The known names
  are the names of the trigonometric and hyperbolic functions, ``exp``,
  ``ln``, ``log``, ``lg``, ``min``, ``max``, ``sqrt``, ``abs``, ``sign`` (or
  ``sgn``), ``Re``, ``Im``, ``arg``, ``erf``, ``erfc``, ``sinc``, ``det``,
  ``tr`` (or ``trace``) and ``adj`` (or ``adjugate``). Apart from ``min`` and
  ``max``, the known functions take one argument. Commands like ``\Re``,
  ``\Im`` and ``\arg`` are not supported on their own, so the real part is
  written as ``\operatorname{Re}(z)``.
* Other readings of the constants and of the functions can be chosen with the
  ``locals`` argument of ``parse_latex_lark``: with
  ``locals={r"\pi": Symbol("pi")}`` the command `\pi` is a symbol and not
  the constant.
* All types of fractions (``\frac``, ``\tfrac``, ``\dfrac``, ``\nicefrac``) and
  binomials (``\binom``, ``\tbinom``, ``\dbinom``) are supported.
* Integrals, both definite and indefinite. When the integrand is a fraction,
  having the differential in the numerator is allowed. The differential is
  allowed to be ``d``, ``\text{d}``, or ``\mathrm{d}``. Double and triple
  integrals can be written by repeating ``\int``, like
  `\int_0^1 \int_0^2 f \, dx \, dy`, where the innermost integral is the one
  next to the integrand.
* Derivatives in one variable, like `\dfrac{d}{dx} (\sin x)`, `\dfrac{dy}{dx}`
  and `\dfrac{d^2}{dx^2} x^3`. The differential has to be a plain ``d``.
  Partial derivatives are not supported yet. Outside of derivatives and
  integrals, ``d`` is an ordinary symbol, so `dx` on its own is ``d*x``, and
  `\dfrac{dx}{x}` outside of an integral simplifies to ``d``.
* Limits in one variable. E.g., `\lim\limits_{t\to 3^{+}} \sin t`.
* Sums and products with simple conditions. For example, `\sum\limits_{k=0}^n k^2`
  is allowed because the condition on `k` is simple. An expression like
  `\sum\limits_{d \mid n} d^2` is not allowed because the condition on `d` in
  the subscript is complicated. The index variable cannot be repeated in the
  superscript, so `\prod\limits_{k=0}^{k=n} k^2` is not allowed, but
  `\prod\limits_{k=0}^{n} k^2` is.
* Bra (e.g., `| x \rangle`), and Ket (e.g., `\langle p |`) notation. Parsing
  Inner (e.g., `\langle x | y \rangle`) and Outer Products (e.g.,
  `| y \rangle \langle x |`) is also supported.

Here is a(n incomplete) list of things which are currently not supported, which
may be added in the future:

* Partial derivatives.
* The ``\iint`` and ``\iiint`` commands for double and triple integrals.

Lark `\mathrm{\LaTeX}` Parser Function Arguments
""""""""""""""""""""""""""""""""""""""""""""""""

Functions like `\sin`, `\ln` and `\exp` are often written without parentheses,
as in `\sin x`. In that case, it is not always clear how much of what follows
is the argument of the function. The Lark-based parser reads it as follows:

* A number followed by symbols is one argument, so `\sin 2x` is ``sin(2*x)``.
* Another function ends the argument, so `\sin x \cos y` is
  ``sin(x)*cos(y)``, while `\sin \cos x` is ``sin(cos(x))``.
* Operators end the argument, so `\sin x + y`, `\sin x / y` and
  `\sin x \cdot y` apply the sine to `x` alone.
* An argument in parentheses ends there, so `\sin(x) y` is ``sin(x)*y``.
* Symbols that follow each other, like `\sin xy` or `\sin x y`, are ambiguous,
  and give the two readings ``sin(x*y)`` and ``y*sin(x)``.
* A power after the argument is also ambiguous, so both `\sin x^2` and
  `\sin(x)^2` give the two readings ``sin(x**2)`` and ``sin(x)**2``. Writing
  `\sin^2 x` or `\sin(x^2)` avoids this.

Lark `\mathrm{\LaTeX}` Parser Matrices
""""""""""""""""""""""""""""""""""""""

The Lark-based LaTeX parser also supports parsing matrices. However, there are
certain assumptions built into the default parser, which we must keep in mind
if we wish to extract the full value out of it.

Matrix Parsing
~~~~~~~~~~~~~~

Matrices inside a ``bmatrix``, ``pmatrix``, ``matrix``, and ``array`` environments
are supported. The ``bmatrix`` and ``pmatrix`` environments can be used on their
own, but the ``matrix`` and ``array`` environments have to be surrounded by
parentheses or brackets, like ``\left( \begin{matrix} ... \end{matrix} \right)``
or ``[\begin{array}{cc} ... \end{array}]``, since they do not draw any delimiters
themselves. The ``smallmatrix`` environment is not supported.

For example::

  parse_latex(r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}", backend="lark")

gives us ::

  Matrix([
  [1, 2],
  [3, 4]])

The Lark-based parser also supports parsing multiline matrix definitions. For example, ::

  s = r"""
  \begin{bmatrix}
  \cos \theta & -\sin \theta \\
  \sin \theta & \cos \theta
  \end{bmatrix}
  """

  parse_latex(s, backend="lark")

gives us the output of ::

  Matrix([
  [cos(theta), -sin(theta)],
  [sin(theta),  cos(theta)]])

Matrix Operations
~~~~~~~~~~~~~~~~~

Basic matrix operations between matrices like matrix-matrix addition and subtraction,
multiplying a matrix by a scalar, and matrix-matrix multiplication are supported.
The results are not evaluated. For example, ::

  parse_latex(r"\begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix} + \begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}", backend="lark")

returns a ``MatAdd`` of the two matrices instead of the sum. Calling ``.doit()``
on the result computes it.

Other common matrix operations are also supported:

* Transpose (usually denoted by raising a matrix to a superscript of `T`). The
  default parser supports the superscript of `T`, as well as primes like
  ``A'`` and ``A^\prime``. An even number of primes, like ``A''``, gives back the
  matrix itself. Other notations like ``A^\top``, ``A^\intercal`` and
  ``A^{\mathsf{T}}`` are not supported. For example, ::

    parse_latex(r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}^T", backend="lark")

  returns the unevaluated transpose ``Transpose(Matrix([[1, 2], [3, 4]]))``.
  Calling ``.doit()`` on it gives ::

    Matrix([
    [1, 3],
    [2, 4]])

* Conjugate transpose (often denoted by raising a matrix to a superscript
  of `H`). The default parser supports the superscript of `H`, as well as stars
  like ``A^{*}`` and ``A^\ast``. The star has to be in braces or written as
  ``\ast``, since ``A^*`` does not parse. An even number of stars gives back the
  matrix itself. ``A^\dagger`` is not supported. Unlike the transpose, the
  conjugate transpose is evaluated. For example, ::

    parse_latex(r"\begin{pmatrix} 1 & \imaginaryunit \\ 3 & 4 \end{pmatrix}^H", backend="lark")

  returns ::

    Matrix([
    [ 1, 3],
    [-I, 4]])

  as expected.
* Traces: The default parser supports ``\operatorname{tr}``,
  ``\operatorname{trace}`` and `\backslash \mathrm{trace}` for the trace. The
  trace is not evaluated, so the result is a ``Trace`` of the matrix. Calling
  ``.doit()`` on it computes the trace.
* Adjugates: The default parser supports ``\operatorname{adj}``,
  ``\operatorname{adjugate}`` and `\backslash \mathrm{adjugate}` for the
  adjugate. The adjugate is evaluated.
* Determinants: The parser supports parsing `\det`, ``\operatorname{det}``, as
  well as `\begin{vmatrix} \dots \end{vmatrix}` as a determinant. The
  determinant is evaluated. For example, both ::

    parse_latex(r"\det(\begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix})", backend="lark")

  and ::

    parse_latex(r"\begin{vmatrix} 1 & 2 \\ 3 & 4 \end{vmatrix}", backend="lark")

  give us an output of `-2`.

Lark `\mathrm{\LaTeX}` Parser Functions
"""""""""""""""""""""""""""""""""""""""

.. autofunction:: sympy.parsing.latex.parse_latex_lark

.. autofunction:: sympy.parsing.latex.parse_latex_lark_all

Lark `\mathrm{\LaTeX}` Parser Classes
"""""""""""""""""""""""""""""""""""""

.. autoclass:: sympy.parsing.latex.lark.LarkLaTeXParser

.. autoclass:: sympy.parsing.latex.lark.TransformToSymPyExpr

`\mathrm{\LaTeX}` Parsing Exceptions Reference
----------------------------------------------

.. autoclass:: sympy.parsing.latex.LaTeXParsingError
   :members:

Experimental SMT-LIB Parsing
----------------------------

.. warning::

   The SMT-LIB parser is still under heavy development. The ``parse_smtlib``
   function is entirely experimental, and its API may change in future
   versions of SymPy.

The SMT-LIB parser is based on `Lark <https://lark-parser.readthedocs.io/en/latest/>`_,
so the ``lark`` Python package needs to be installed in order to use it.

SMT-LIB Parsing Functions Reference
-----------------------------------

.. autofunction:: sympy.parsing.smtlib.parse_smtlib

SMT-LIB Parsing Exceptions Reference
------------------------------------

.. autoclass:: sympy.parsing.smtlib.SMTLibSyntaxError
   :members:

.. autoclass:: sympy.parsing.smtlib.UnknownSMTLibCommandError
   :members:

.. autoclass:: sympy.parsing.smtlib.UnknownSMTLibOperatorError
   :members:

SymPy Expression Reference
--------------------------

.. module:: sympy.parsing.sym_expr

.. autoclass:: SymPyExpression
   :members:

Runtime Installation
--------------------

The currently-packaged LaTeX parser backend is partially generated with
`ANTLR4 <https://www.antlr.org/>`_,
but to use the parser, you only need the ``antlr4`` Python package available.

Depending on your package manager, you can install the right package with, for
example, ``pip``::

    $ pip install antlr4-python3-runtime==4.11

or ``conda``::

    $ conda install -c conda-forge antlr-python-runtime==4.11

The C parser depends on ``clang`` and the Fortran parser depends on ``LFortran``.
You can install these packages using::

    $ conda install -c conda-forge lfortran clang
