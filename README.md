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

## Programming Constructs Currently Supported in Playground
* importing code from other modules (.plgd files)
    * Absolute paths and relative paths are supported for importing Playground modules
    * For relative paths: paths should always be relative to the file the import statement is in. See the example below
    ```
    Dir structure:

    src \
        foo_dir \
            foo.plgd
        bar_dir \
            bar.plgd

    In foo.plgd, bar.plgd is imported like this:

       import "..\\bar_dir\\bar.plgd"
    ```
    * Like in Python, in Playground any code found in the imported module is RUN as a part of the import process, so be careful about putting statements at the top level in modules you intend to import
    * Currently, ALL code from a module is imported to the current file when an import occurs. Future releases may allow selective importing of items from modules

* Comments using the '#' symbol
    * Comments can exist on their own line, or on the same line as a statement:
    ```
    # A comment on it's own line!
    print("Hello world"); # A comment on the same line as a statement!
    ```

* Data types: Int, Float, Bools, Strings:
    ```
    a = 0;          # int 
    b = 0.0;        # Float
    c = True;       # Bool
    c = False;      # Bool
    c = "A string"; 
    ```
* Addition, subtraction, multiplication, division on said basic data types 
    * There is implicit conversion on types, since the types are basically python types
    ```
    a = 2 * 3;  # -> 6, an int 
    b = 2 * 1.5 # -> 3.0, a Float 
    c = 3 / 2   # -> 
    ```
* Boolean expressions, (comparison operators, 'and' 'or' etc)
    ```
    a = 10; b = 5;
    a <= b;
    ```
* Conditional statements (if, elif, else, while)
    ```
    a = 5; b = 10;
    if (a <= 10){
        print("a <= 10");
    }
    elif (a > b){
        print("a > b");
    }
    else{
        print("Impossible to reach here");
    }

    while (a <= b){
        a = a + 1;
        print(a);
    }

   if (
        (a < b and b == 10)
        or (a > b and a == 11)
    )
    {
        print("stuff");
    }
    ```
* Nested scopes (block statements)
    ```
    # Global scope 
    print("I'm in global scope!");

    b = 3;
    a = 5;
    {
        # Nested scope
        print("I'm in a nested scope!");
        print("a from global scope: ", a); # -> prints '5'
        b = 10;
    }
    print("b is: ", b); # -> prints '3'

    Class foo{
        # Class scope 
        print("I'm in a class scope!");
    }
    ```
* Functions (including returning values from funcs)
    * Two functions can share the same name, provided they have a different number of arguments
    ```
    def func_foo(a, b){
        print("I have parameters a and b: , a, " ", b);
    }
    func_foo(1, 2); # -> prints "I have parameters a and b: 1 2"

    def no_params(){
        print("no_params(): I have no params");
    }

    def func_foo(){
        print("I'm also func_foo, but I have no params");
    }
    ```
* User defined data types, e.g. classes. Structs are also supported as they are a subset of classes
    ```
    Class Foo {
        bar; # Do not have to give fields a default value 
        zar = 10; 

        def Foo(){
            bar = 10;
            zar = 20;
        }

        # If you used this constructor, bar will be give the value of None
        def Foo(z){
            zar = z;
        }

        # If a func param will shadow a class field, using keyword 'this' will allow you to access said class field inside the func
        def Foo(bar, zar){
            this.bar = bar;
            this.zar = zar;
        }

        def a_method(a_param){
            print("a_param ", a_param);
        }
    }

    goo = Foo();
    print(goo.bar);
    goo.a_method("This is a string");

    moo = Foo(10);
    moo.bar = 20;
    k = moo.zar;

    moo = Foo(23, "Not an int");
    print(moo.attrs); # -> prints '{'bar': 20, 'zar': 10}'
    ```

To-Add List:
* Forward references
* Improved strings (being able to escape chars, string subsitution etc)
* Static methods for user classes

Ideally, I would like to get this project to a point where I could start implementing features in _playground_ itself. I'm not sure how much I would actually do, but being able to _start_ using the lang itself to add to the lang would be pretty cool.

Future experiments I may decide to try with this project might include:
* Selective importing of items from modules
* Byte code interpreter
* Adding a REPL
* Use ANTLR to generate the parser (it can target Python, and has a Python runtime)