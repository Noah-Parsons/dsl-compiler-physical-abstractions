# DSL Compiler for Physical Abstractions

This repository contains an early-stage implementation of a domain-specific language (DSL) compiler designed for the formal representation and transformation of physical systems. It integrates symbolic parsing, dimensional type checking, and category-theoretic abstraction to model physical quantities, laws, and symmetries.

## Overview

The compiler parses LaTeX-inspired DSL syntax into an abstract syntax tree (AST), applies physical unit consistency checks, and compiles the result into an intermediate representation (IR) grounded in category theory. This IR captures physical quantities as objects and physical laws as morphisms, enabling symbolic reasoning and future integration with numerical solvers and formal verification tools.

## Features

- **Custom DSL Syntax**  
  Support for LaTeX-style commands (`\defvar`, `\define`, `\boundary`, `\symmetry`) to define variables, equations, and symmetries.

- **Lexer and Parser**  
  Recursive-descent parser with full expression support including operator precedence and parenthetical grouping.

- **Dimensional Type System**  
  Static type checker with unit inference and dimensional analysis to ensure physical consistency.

- **Categorical Intermediate Representation**  
  Encodes physical structures using category-theoretic constructs (objects, morphisms, identity, composition), enabling formal reasoning.

- **Extensible Architecture**  
  Designed for future phases including differential operator support, symbolic simulation, theorem proving, and code generation.

## Example Input (DSL)

```latex
\defvar{T}{Real}{kelvin}
\defvar{k}{Real}{1}
\define{ \op{laplace}(T) = k * T^2 + 3.14 * T - 1.0 }
\boundary{T}
\symmetry{Noether \invariant energy}


Output Pipeline
Tokenization — Breaks DSL input into token stream.

Parsing — Constructs abstract syntax tree.

Type Checking — Ensures unit consistency.

IR Generation — Translates program into categorical IR (objects and morphisms).

Pretty Print — Displays IR summary including morphism domains, codomains, and descriptors.

Future Work
This compiler represents the foundation of a multi-phase project. Planned expansions include:



Target Applications:
Formal modeling of physical systems

Physics-aware compilers and symbolic engines

Automatic derivation of physical consequences from axioms

Categorical reasoning in physics and computation

Educational tools and research instrumentation

Repository Structure
.
├── enhanced_phase_1_1_dsl_compiler.py   # Main compiler source file
├── README.md                            # Project documentation
License
This project is released under the MIT License. See the LICENSE file for details.

Contact
For collaboration, feedback, or research inquiries, please open an issue or contact the repository maintainer.
