This project is a small programming language made by me, to explore the patterns and topics found in this book: "[Language Implementation Patterns:
Create Your Own Domain-Specific and General Programming Languages"
by Terence Parr](https://pragprog.com/titles/tpdsl/language-implementation-patterns/). 

All implementation is done in Python. Python is not the best choice for implementing a programming language, but again my primary motivation behind doing this project was to explore the patterns in the book; So I decided to go with a lang that's fast to work with. 

It is a dynamically typed language which copies its syntax heavily from Python (with the exception of white space being significant).

In it's current form, it is made up of a hand built parser, which generates an AST, which I then feed to a hand-written high level interpreter.

Current programing constructs that it supports:
* Data types: Int, Float, Bools
* Addition, subtraction, multiplication, division on said basic data types 
* Boolean expressions
* Conditional statements (if, elif, else, while)
* Nested scopes (block statements)

Next on the list to be added:
* Data type: Strings
* functions
* Forward references
* User defined data types (classes or structs, or both)

Ideally, I would like to get this project to a point where I could start implementing features in _playground_ itself. I'm not sure how much I would actually do, but being able to _start_ using the lang itself to add to the lang would be pretty cool.

Future experiments I may decide to try with this project might include:
* Byte code interpreter
* Adding a REPL
* Use ANTLR to generate the parser (it can target Python, and has a Python runtime)