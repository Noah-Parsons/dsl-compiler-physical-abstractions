# -*- coding: utf-8 -*-
"""Enhanced Phase 1.1: DSL Compiler for Physical Abstractions.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1c4eVP0eNQZIUdyf_aq7tpuLw7JB6Y91t
"""

# === Enhanced Phase 1.1: DSL Compiler for Physical Abstractions ===

import re
from typing import List, Union, Tuple, Dict, Optional
from enum import Enum
from dataclasses import dataclass

# === Enhanced Token Types ===
TOKEN_TYPES = [
    ("COMMAND", r"\\[a-zA-Z]+"),          # LaTeX-style command
    ("LBRACE", r"\{"),                    # Left curly brace
    ("RBRACE", r"\}"),                    # Right curly brace
    ("LPAREN", r"\("),                    # Left parenthesis
    ("RPAREN", r"\)"),                    # Right parenthesis
    ("PLUS", r"\+"),                      # Addition operator
    ("MINUS", r"-"),                      # Subtraction operator
    ("MULTIPLY", r"\*"),                  # Multiplication operator
    ("DIVIDE", r"/"),                     # Division operator
    ("POWER", r"\^"),                     # Exponentiation operator
    ("EQUALS", r"="),                     # Equals sign
    ("COMMA", r","),                      # Comma separator
    ("NUMBER", r"\d+(\.\d+)?"),           # Integer or floating-point number
    ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_]*"), # Identifier
    ("WHITESPACE", r"\s+"),               # Whitespace
]

# Combine into one regex with named groups
token_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_TYPES)
token_pattern = re.compile(token_regex)

# === Enhanced Token Class ===
@dataclass
class Token:
    type: str
    value: str
    position: int = 0  # Position in source for better error reporting

    def __repr__(self):
        return f"{self.type}:{self.value}@{self.position}"

# === Enhanced Tokenizer ===
def tokenize(source: str) -> List[Token]:
    tokens = []
    for match in token_pattern.finditer(source):
        kind = match.lastgroup
        value = match.group()
        position = match.start()
        if kind != "WHITESPACE":
            tokens.append(Token(kind, value, position))
    return tokens

# === Enhanced AST Nodes ===
class ASTNode:
    pass

class Expression(ASTNode):
    """Base class for all expressions"""
    pass

class NumberExpr(Expression):
    def __init__(self, value: float):
        self.value = value

    def __repr__(self):
        return f"Num({self.value})"

class IdentExpr(Expression):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Id({self.name})"

class BinaryOpExpr(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"BinOp({self.left} {self.operator} {self.right})"

class UnaryOpExpr(Expression):
    def __init__(self, operator: str, operand: Expression):
        self.operator = operator
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp({self.operator}{self.operand})"

class VarDef(ASTNode):
    def __init__(self, name: str, vartype: str, unit: str):
        self.name = name
        self.vartype = vartype
        self.unit = unit

    def __repr__(self):
        return f"VarDef(name='{self.name}', vartype='{self.vartype}', unit='{self.unit}')"

class Op(ASTNode):
    def __init__(self, name: str, args: List[str]):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"Op(name='{self.name}', args={self.args})"

class Define(ASTNode):
    def __init__(self, lhs: Op, rhs: Expression):
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return f"Define(lhs={self.lhs}, rhs={self.rhs})"

class Boundary(ASTNode):
    def __init__(self, expr: str):
        self.expr = expr

    def __repr__(self):
        return f"Boundary(expr='{self.expr}')"

class Symmetry(ASTNode):
    def __init__(self, law: str, invariant: str):
        self.law = law
        self.invariant = invariant

    def __repr__(self):
        return f"Symmetry(law='{self.law}', invariant='{self.invariant}')"

# === Physical Units System ===
class Unit:
    def __init__(self, dimensions: Dict[str, int]):
        # Dimensions: mass, length, time, temperature, etc.
        self.dimensions = dimensions

    def __mul__(self, other):
        result = {}
        all_dims = set(self.dimensions.keys()) | set(other.dimensions.keys())
        for dim in all_dims:
            result[dim] = self.dimensions.get(dim, 0) + other.dimensions.get(dim, 0)
        return Unit(result)

    def __truediv__(self, other):
        result = {}
        all_dims = set(self.dimensions.keys()) | set(other.dimensions.keys())
        for dim in all_dims:
            result[dim] = self.dimensions.get(dim, 0) - other.dimensions.get(dim, 0)
        return Unit(result)

    def __pow__(self, exponent):
        result = {dim: power * exponent for dim, power in self.dimensions.items()}
        return Unit(result)

    def is_compatible(self, other):
        return self.dimensions == other.dimensions

    def __repr__(self):
        return f"Unit({self.dimensions})"

# Standard units
UNITS = {
    "meter": Unit({"length": 1}),
    "m": Unit({"length": 1}),
    "second": Unit({"time": 1}),
    "s": Unit({"time": 1}),
    "kilogram": Unit({"mass": 1}),
    "kg": Unit({"mass": 1}),
    "kelvin": Unit({"temperature": 1}),
    "K": Unit({"temperature": 1}),
    "dimensionless": Unit({}),
    "1": Unit({}),
    "energy": Unit({"mass": 1, "length": 2, "time": -2}),  # Joules
    "force": Unit({"mass": 1, "length": 1, "time": -2}),   # Newtons
}

# === Enhanced Parser with Expression Support ===
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def match(self, expected_type: str) -> Optional[Token]:
        token = self.peek()
        if token and token.type == expected_type:
            self.pos += 1
            return token
        return None

    def expect(self, expected_type: str) -> Token:
        token = self.match(expected_type)
        if not token:
            current = self.peek()
            if current:
                raise SyntaxError(f"Expected {expected_type} but got {current.type} '{current.value}' at position {current.position}")
            else:
                raise SyntaxError(f"Expected {expected_type} but reached end of input")
        return token

    def parse(self) -> List[ASTNode]:
        nodes = []
        while self.pos < len(self.tokens):
            token = self.peek()
            if token.type == "COMMAND":
                if token.value == r"\defvar":
                    nodes.append(self.parse_defvar())
                elif token.value == r"\define":
                    nodes.append(self.parse_define())
                elif token.value == r"\boundary":
                    nodes.append(self.parse_boundary())
                elif token.value == r"\symmetry":
                    nodes.append(self.parse_symmetry())
                else:
                    raise SyntaxError(f"Unknown command: {token.value} at position {token.position}")
            else:
                self.pos += 1
        return nodes

    def parse_defvar(self) -> VarDef:
        self.expect("COMMAND")  # \defvar
        self.expect("LBRACE")
        name = self.expect("IDENT").value
        self.expect("RBRACE")
        self.expect("LBRACE")
        vartype = self.expect("IDENT").value
        self.expect("RBRACE")
        self.expect("LBRACE")
        # Unit can be either an identifier or a number (for dimensionless quantities)
        unit_token = self.peek()
        if unit_token and unit_token.type == "IDENT":
            unit = self.expect("IDENT").value
        elif unit_token and unit_token.type == "NUMBER":
            unit = self.expect("NUMBER").value
        else:
            raise SyntaxError(f"Expected unit (IDENT or NUMBER) but got {unit_token.type if unit_token else 'EOF'}")
        self.expect("RBRACE")
        return VarDef(name, vartype, unit)

    def parse_define(self) -> Define:
        self.expect("COMMAND")  # \define
        self.expect("LBRACE")

        self.expect("COMMAND")  # \op
        self.expect("LBRACE")
        op_name = self.expect("IDENT").value
        self.expect("RBRACE")

        self.expect("LPAREN")
        args = []
        args.append(self.expect("IDENT").value)
        while self.match("COMMA"):
            args.append(self.expect("IDENT").value)
        self.expect("RPAREN")

        self.expect("EQUALS")

        # Parse the right-hand side expression
        rhs = self.parse_expression()

        self.expect("RBRACE")

        return Define(Op(op_name, args), rhs)

    def parse_expression(self) -> Expression:
        """Parse expressions with operator precedence"""
        return self.parse_additive()

    def parse_additive(self) -> Expression:
        """Parse + and - operators (lowest precedence)"""
        left = self.parse_multiplicative()

        while True:
            if self.match("PLUS"):
                right = self.parse_multiplicative()
                left = BinaryOpExpr(left, "+", right)
            elif self.match("MINUS"):
                right = self.parse_multiplicative()
                left = BinaryOpExpr(left, "-", right)
            else:
                break

        return left

    def parse_multiplicative(self) -> Expression:
        """Parse * and / operators (medium precedence)"""
        left = self.parse_power()

        while True:
            if self.match("MULTIPLY"):
                right = self.parse_power()
                left = BinaryOpExpr(left, "*", right)
            elif self.match("DIVIDE"):
                right = self.parse_power()
                left = BinaryOpExpr(left, "/", right)
            else:
                break

        return left

    def parse_power(self) -> Expression:
        """Parse ^ operator (highest precedence)"""
        left = self.parse_primary()

        if self.match("POWER"):
            right = self.parse_power()  # Right associative
            return BinaryOpExpr(left, "^", right)

        return left

    def parse_primary(self) -> Expression:
        """Parse primary expressions (numbers, identifiers, parentheses)"""
        token = self.peek()

        if self.match("NUMBER"):
            return NumberExpr(float(self.tokens[self.pos - 1].value))

        if self.match("IDENT"):
            return IdentExpr(self.tokens[self.pos - 1].value)

        if self.match("LPAREN"):
            expr = self.parse_expression()
            self.expect("RPAREN")
            return expr

        if self.match("MINUS"):
            operand = self.parse_primary()
            return UnaryOpExpr("-", operand)

        if token:
            raise SyntaxError(f"Unexpected token {token.type} '{token.value}' at position {token.position}")
        else:
            raise SyntaxError("Unexpected end of input")

    def parse_boundary(self) -> Boundary:
        self.expect("COMMAND")  # \boundary
        self.expect("LBRACE")
        expr = self.expect("IDENT").value
        self.expect("RBRACE")
        return Boundary(expr)

    def parse_symmetry(self) -> Symmetry:
        self.expect("COMMAND")  # \symmetry
        self.expect("LBRACE")
        law = self.expect("IDENT").value
        self.expect("COMMAND")  # \invariant
        invariant = self.expect("IDENT").value
        self.expect("RBRACE")
        return Symmetry(law, invariant)

# === Enhanced Type Checker with Dimensional Analysis ===
class TypeChecker:
    def __init__(self):
        self.variables: Dict[str, Tuple[str, Unit]] = {}
        self.operators: Dict[str, Tuple[List[str], str]] = {}

    def get_unit(self, unit_str: str) -> Unit:
        """Convert unit string to Unit object"""
        if unit_str in UNITS:
            return UNITS[unit_str]
        elif unit_str in ["1", "1.0"] or unit_str.replace(".", "").isdigit():
            # Handle numeric units as dimensionless
            return UNITS["dimensionless"]
        else:
            # For unknown units, create a custom unit
            return Unit({unit_str: 1})

    def check_expression_type(self, expr: Expression) -> Unit:
        """Check the dimensional consistency of an expression"""
        if isinstance(expr, NumberExpr):
            return UNITS["dimensionless"]

        elif isinstance(expr, IdentExpr):
            if expr.name not in self.variables:
                raise TypeError(f"Undefined variable: {expr.name}")
            _, unit = self.variables[expr.name]
            return unit

        elif isinstance(expr, BinaryOpExpr):
            left_unit = self.check_expression_type(expr.left)
            right_unit = self.check_expression_type(expr.right)

            if expr.operator == "+":
                if not left_unit.is_compatible(right_unit):
                    raise TypeError(f"Cannot add incompatible units: {left_unit} + {right_unit}")
                return left_unit

            elif expr.operator == "-":
                if not left_unit.is_compatible(right_unit):
                    raise TypeError(f"Cannot subtract incompatible units: {left_unit} - {right_unit}")
                return left_unit

            elif expr.operator == "*":
                return left_unit * right_unit

            elif expr.operator == "/":
                return left_unit / right_unit

            elif expr.operator == "^":
                if not isinstance(expr.right, NumberExpr):
                    raise TypeError("Exponent must be a number")
                return left_unit ** expr.right.value

        elif isinstance(expr, UnaryOpExpr):
            operand_unit = self.check_expression_type(expr.operand)
            if expr.operator == "-":
                return operand_unit

        raise TypeError(f"Unknown expression type: {type(expr)}")

    def check(self, ast: List[ASTNode]):
        print("\n[Enhanced TypeCheck] Starting type checking...")

        # First pass: collect variable definitions
        for node in ast:
            if isinstance(node, VarDef):
                unit = self.get_unit(node.unit)
                self.variables[node.name] = (node.vartype, unit)
                print(f"[TypeCheck] {node.name}: type = {node.vartype}, unit = {unit}")

        # Second pass: check definitions and expressions
        for node in ast:
            if isinstance(node, Define):
                if isinstance(node.lhs, Op):
                    # Check that all arguments are defined
                    for arg in node.lhs.args:
                        if arg not in self.variables:
                            raise TypeError(f"Undefined variable in operator: {arg}")

                    # Check dimensional consistency of RHS
                    try:
                        rhs_unit = self.check_expression_type(node.rhs)
                        print(f"[TypeCheck] Definition {node.lhs.name} has result unit: {rhs_unit}")
                    except Exception as e:
                        print(f"[TypeCheck] Warning in definition {node.lhs.name}: {e}")
                        # Continue processing rather than stopping on dimensional analysis errors

            elif isinstance(node, Boundary):
                if node.expr not in self.variables:
                    raise TypeError(f"Boundary references undefined variable: {node.expr}")
                print(f"[TypeCheck] Boundary condition on: {node.expr}")

            elif isinstance(node, Symmetry):
                print(f"[TypeCheck] Symmetry declared: {node.law} invariant under {node.invariant}")

# === Enhanced IR Compiler with Category Theory ===
class CategoricalIR:
    def __init__(self):
        self.objects: Dict[str, Dict] = {}
        self.morphisms: List[Tuple[str, str, str, str, Dict]] = []
        self.functors: List[Dict] = []

    def add_object(self, name: str, properties: Dict):
        """Add an object to the category"""
        self.objects[name] = properties

    def add_morphism(self, name: str, domain: str, codomain: str, description: str, properties: Dict = None):
        """Add a morphism to the category"""
        if properties is None:
            properties = {}
        self.morphisms.append((name, domain, codomain, description, properties))

    def add_functor(self, name: str, source_category: str, target_category: str, object_map: Dict, morphism_map: Dict):
        """Add a functor between categories"""
        self.functors.append({
            "name": name,
            "source": source_category,
            "target": target_category,
            "object_map": object_map,
            "morphism_map": morphism_map
        })

    def compose_morphisms(self, f_name: str, g_name: str) -> Optional[str]:
        """Attempt to compose two morphisms f;g"""
        f_morph = next((m for m in self.morphisms if m[0] == f_name), None)
        g_morph = next((m for m in self.morphisms if m[0] == g_name), None)

        if f_morph and g_morph and f_morph[2] == g_morph[1]:  # codomain(f) == domain(g)
            comp_name = f"{f_name}_{g_name}"
            comp_desc = f"Composition of {f_morph[3]} and {g_morph[3]}"
            self.add_morphism(comp_name, f_morph[1], g_morph[2], comp_desc)
            return comp_name
        return None

class IRCompiler:
    def __init__(self):
        self.ir = CategoricalIR()

    def compile(self, ast: List[ASTNode]):
        print("\n[Enhanced IR] Compiling to Enhanced Categorical IR...")

        # Process variable definitions as objects
        for node in ast:
            if isinstance(node, VarDef):
                self.ir.add_object(node.name, {
                    "type": node.vartype,
                    "unit": node.unit,
                    "category": "PhysicalQuantity"
                })

        # Process definitions as morphisms
        for node in ast:
            if isinstance(node, Define):
                if isinstance(node.lhs, Op):
                    morphism_name = f"define_{node.lhs.name}"
                    domain = node.lhs.args[0] if node.lhs.args else "Unknown"
                    codomain = domain  # Could be refined based on return type analysis
                    law_desc = f"{node.lhs.name}({', '.join(node.lhs.args)}) = {self.expr_to_string(node.rhs)}"

                    self.ir.add_morphism(morphism_name, domain, codomain, law_desc, {
                        "type": "PhysicalLaw",
                        "operator": node.lhs.name,
                        "arity": len(node.lhs.args)
                    })

            elif isinstance(node, Boundary):
                var = node.expr
                self.ir.add_morphism(f"boundary_{var}", var, "BoundarySpace", "Boundary condition", {
                    "type": "BoundaryCondition"
                })

            elif isinstance(node, Symmetry):
                self.ir.add_morphism(f"symmetry_{node.law}", "SymmetryGroup", "SymmetryGroup",
                                   f"Invariant under {node.invariant}", {
                    "type": "Symmetry",
                    "law": node.law,
                    "invariant": node.invariant
                })

        # Add identity morphisms for all objects
        for obj_name in self.ir.objects:
            self.ir.add_morphism(f"id_{obj_name}", obj_name, obj_name, f"Identity on {obj_name}", {
                "type": "Identity"
            })

        self.pretty_print()

    def expr_to_string(self, expr: Expression) -> str:
        """Convert expression AST back to string representation"""
        if isinstance(expr, NumberExpr):
            return str(expr.value)
        elif isinstance(expr, IdentExpr):
            return expr.name
        elif isinstance(expr, BinaryOpExpr):
            left_str = self.expr_to_string(expr.left)
            right_str = self.expr_to_string(expr.right)
            return f"({left_str} {expr.operator} {right_str})"
        elif isinstance(expr, UnaryOpExpr):
            operand_str = self.expr_to_string(expr.operand)
            return f"{expr.operator}{operand_str}"
        return str(expr)

    def pretty_print(self):
        print("\n[Enhanced IR] Objects:")
        for obj, props in self.ir.objects.items():
            print(f" - {obj} : {props['type']} [{props['unit']}] in {props['category']}")

        print("\n[Enhanced IR] Morphisms:")
        for name, domain, codomain, desc, props in self.ir.morphisms:
            morph_type = props.get('type', 'Unknown')
            print(f" - {name}: {domain} -> {codomain} | {desc} [{morph_type}]")

        print("\n[Enhanced IR] Categorical Properties:")
        print(f" - Objects: {len(self.ir.objects)}")
        print(f" - Morphisms: {len(self.ir.morphisms)}")
        print(f" - Functors: {len(self.ir.functors)}")

# === Enhanced Example Usage ===
def run_enhanced_compiler():
    # Enhanced DSL example with mathematical expressions
    dsl = r"""
    \defvar{T}{Real}{kelvin}
    \defvar{k}{Real}{1}
    \defvar{t}{Real}{s}
    \define{ \op{laplace}(T) = k * T^2 + 3.14 * T - 1.0 }
    \define{ \op{heat_flux}(T, k) = -k * T }
    \boundary{T}
    \symmetry{Noether \invariant energy}
    """

    print("=== Enhanced DSL Compiler Demo ===")
    print(f"Source DSL:\n{dsl}")

    try:
        # Tokenization
        tokens = tokenize(dsl)
        print("\n[Tokens]")
        for token in tokens:
            print(f" - {token}")

        # Parsing
        parser = Parser(tokens)
        ast = parser.parse()

        print("\n[Enhanced AST]")
        for stmt in ast:
            print(f" - {stmt}")

        # Type Checking with Dimensional Analysis
        checker = TypeChecker()
        checker.check(ast)

        # IR Compilation
        compiler = IRCompiler()
        compiler.compile(ast)

    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")

# Run the enhanced compiler
if __name__ == "__main__":
    run_enhanced_compiler()