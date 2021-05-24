This project is a small programming language made by me, to explore the patterns and topics found in this book: "[Language Implementation Patterns:
Create Your Own Domain-Specific and General Programming Languages"
by Terence Parr](https://pragprog.com/titles/tpdsl/language-implementation-patterns/). 

All implementation is done in Python. Python is not the best choice for implementing a programming language, but again my primary motivation behind doing this project was to explore the patterns in the book; So I decided to go with a lang that's fast to work with. 

It is a dynamically typed language which copies its syntax heavily from Python (with the exception of white space being significant).

In it's current form, it is made up of a hand built parser, which generates an AST, which I then feed to a hand-written high level interpreter.

Because the interpreter is written in Python, I do not have to directly handle a lot of the difficult implementation details.
I can lean on Python's typing system, Exception system, object system, etc etc, to be my backend for my types, my functions, my errors etc. 

I would _maybe_ like to change this in the future, but right now this is necessary since I want to focus on the bigger details of language implementation. 

If I was to switch to a different language, like C or Java, I would have to put in a considerable amount of more work into my backend.

Current programing constructs that it supports:
* Data types: Int, Float, Bools, Strings
* Addition, subtraction, multiplication, division on said basic data types 
* Boolean expressions
* Conditional statements (if, elif, else, while)
* Nested scopes (block statements)
* Functions
* User defined data types, e.g. classes. Structs are also supported as they are a subset of classes

Next on the list to be added:
* Improved strings (being able to escape chars, string subsitution etc)
* Forward references
* Static methods for user classes

Ideally, I would like to get this project to a point where I could start implementing features in _playground_ itself. I'm not sure how much I would actually do, but being able to _start_ using the lang itself to add to the lang would be pretty cool.

Future experiments I may decide to try with this project might include:
* Byte code interpreter
* Adding a REPL
* Use ANTLR to generate the parser (it can target Python, and has a Python runtime)