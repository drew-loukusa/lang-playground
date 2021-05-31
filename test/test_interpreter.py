import sys

sys.path.append("c:\\src\\lang-playground\\playground")

import pytest
from playground_interpreter import PlaygroundInterpreter


def run_stdout_test(capfd, in_str, ans_str):
    in_str = in_str.strip()
    ans_str = ans_str.strip()
    pgp = PlaygroundInterpreter()
    pgp.interp(input_str=in_str)
    out, err = capfd.readouterr()
    if '\n' not in ans_str:
        assert out.strip() == ans_str.strip()
    else:
        for a,b in zip(out.split('\n'), ans_str.split('\n')):
            assert a.strip() == b.strip()

# Test math operations
def test_add_1(capfd):
    run_stdout_test(capfd, "print(5+5);", "10")


def test_add_2(capfd):
    run_stdout_test(capfd, "print(25+15);", "40")


def test_sub_1(capfd):
    run_stdout_test(capfd, "print(5-5);", "0")


def test_sub_2(capfd):
    run_stdout_test(capfd, "print(25-9);", "16")


def test_mul_1(capfd):
    run_stdout_test(capfd, "print(5*5);", "25")


def test_mul_2(capfd):
    run_stdout_test(capfd, "print(10*10);", "100")


def test_div_1(capfd):
    run_stdout_test(capfd, "print(5/2);", "2.5")


def test_div_2(capfd):
    run_stdout_test(capfd, "print(100/10);", "10.0")


# Test Boolean expressions
def test_bool_1(capfd):
    in_str = "print(True);"
    ans_str = "True"
    run_stdout_test(capfd, in_str, ans_str)


def test_bool_2(capfd):
    in_str = "print(False);"
    ans_str = "False"
    run_stdout_test(capfd, in_str, ans_str)


def test_bool_3(capfd):
    in_str = "print( ((5 + 3) > 2) );"
    ans_str = "True"
    run_stdout_test(capfd, in_str, ans_str)


# Test AND, OR
def test_bool_4(capfd):
    in_str = "print( (True and True ));"
    ans_str = "True"
    run_stdout_test(capfd, in_str, ans_str)


def test_bool_5(capfd):
    in_str = "print( (False and True ));"
    ans_str = "False"
    run_stdout_test(capfd, in_str, ans_str)


def test_bool_6(capfd):
    in_str = "print( (True and False ));"
    ans_str = "False"
    run_stdout_test(capfd, in_str, ans_str)


def test_bool_7(capfd):
    in_str = "print( (False or True) );"
    ans_str = "True"
    run_stdout_test(capfd, in_str, ans_str)


def test_bool_8(capfd):
    in_str = "print( (False or False) );"
    ans_str = "False"
    run_stdout_test(capfd, in_str, ans_str)


def test_bool_9(capfd):
    in_str = "print( (False and False) );"
    ans_str = "False"
    run_stdout_test(capfd, in_str, ans_str)


def test_bool_9(capfd):
    in_str = "print(False and False);"
    ans_str = "False"
    run_stdout_test(capfd, in_str, ans_str)


# Test scoping rules
def test_nested_1(capfd):
    in_str = """
    a = 10;
    {
        print(a);
        a = 5;
    }
    """
    run_stdout_test(capfd, in_str, "10")


def test_nested_2(capfd):
    in_str = """
    a = 10;
    {
        a = 5;
        print(a);
    }
    """
    run_stdout_test(capfd, in_str, "5")


# Test Conditional
def test_cond_1(capfd):
    in_str = "if(True){print(True);}"
    ans_str = "True"
    run_stdout_test(capfd, in_str, ans_str)


def test_cond_2(capfd):
    in_str = 'if(False){print("False");}else{print("True");}'
    ans_str = "True"
    run_stdout_test(capfd, in_str, ans_str)


def test_cond_3(capfd):
    in_str = 'if(False){print("False");}elif(True){print("True");}'
    ans_str = "True"
    run_stdout_test(capfd, in_str, ans_str)


# Functions
def test_func_1(capfd):
    in_str = """
    def foo(){
        print("foo called");
    }
    foo();
    """
    ans_str = "foo called"
    run_stdout_test(capfd, in_str, ans_str)


def test_func_2(capfd):
    in_str = """
    def foo(a){
        print("foo called, a: ", a);
    }
    foo(5);
    """
    ans_str = "foo called, a: 5"
    run_stdout_test(capfd, in_str, ans_str)


def test_func_3(capfd):
    in_str = """
    def foo(a){
        print("foo called, a: ", a);
    }
    {
        foo(5);
    }
    """
    ans_str = "foo called, a: 5"
    run_stdout_test(capfd, in_str, ans_str)


def test_func_4(capfd):
    in_str = """
    def foo(a){
        print("foo called, a: ", a);
    }
    foo();
    """
    with pytest.raises(TypeError):
        pgp = PlaygroundInterpreter()
        pgp.interp(input_str=in_str)


def test_func_5(capfd):
    in_str = """
    def foo(a){
        print("foo called, a: ", a);
    }
    foo(5, 10);
    """
    with pytest.raises(TypeError):
        pgp = PlaygroundInterpreter()
        pgp.interp(input_str=in_str)


def test_func_6(capfd):
    in_str = """
    def outer(outA){
        def inner(inA){
            print("Inner a: ", inA);
        }
        inner(10);
        print("outer a: ", outA);
    }
    outer(15);
    inner(10);
    """
    with pytest.raises(NameError):
        pgp = PlaygroundInterpreter()
        pgp.interp(input_str=in_str)

# Class Testing
def test_class_1(capfd):
    in_str = """import "..\\examples\\ex_module_Point.plgd";
    k = Point(10, 10);
    f = Point(20, 5);
    p = k.Add(f);
    print(p.to_str());"""
    ans_str = "<Point: (30, 15)>"
    run_stdout_test(capfd, in_str, ans_str)

def test_class_2(capfd):
    in_str = """
    import "..\\examples\\ex_module_foo_class.plgd";
    instance_foo = FooClass(10);
    instance_foo = FooClass();
    instance_foo.NotAConstructor();
    print("Accessing class attr outside the class: ", instance_foo.class_attr_a);
    instance_foo.class_attr_a = 10;
    print("After changing it: ", instance_foo.class_attr_a);
    print("instance_foo.bar: ", instance_foo.bar);
    instance_foo.func_with_shadowing_param(5);
    print("instance_foo.bar: ", instance_foo.bar);
    print("5 % 3 == ", 5 % 3);
    """

    ans_str = """
    Constructor called! I have one arg!
    Assign a to 'class_attr_a' !
    class_attr_a before: 5
    class_attr_a: 10
    Empty constructor!
    class_attr_b: None
    class_attr_a: 5
    I don't have any params, and I'm not a constructor     
    here's class_attr_a: 5
    Accessing class attr outside the class: 5
    After changing it: 10
    instance_foo.bar: 1
    shadowing func param bar is: 12
    Printing shadowed class attr using keyword 'this': 1   
    Set shadowed class attr bar to 15
    instance_foo.bar: 15
    5 % 3 == 2
    """
    run_stdout_test(capfd, in_str, ans_str)

def test_nested_class_1(capfd):
    in_str = """
    Class Outer {
        a = 0;
        b = 1;
        
        Class Inner {
            ai = 234;
            bi = 0;

            def Inner(ai, bi){
                this.ai = ai;
                this.bi = bi;
            }
        }
    }
    print(Outer.Inner.ai);    
    out_in = Outer.Inner(500, 99);
    print(out_in);

    out = Outer();
    in = out.Inner(7, 8);
    print(out);
    print(in);
    """
    
    ans_str = """
    234
    <Instance of Class: Inner, attrs: {'ai': 500, 'bi': 99} >
    <Instance of Class: Outer, attrs: {'a': 0, 'b': 1} >
    <Instance of Class: Inner, attrs: {'ai': 7, 'bi': 8} >
    """
    run_stdout_test(capfd, in_str, ans_str)

def test_nested_class_2(capfd):
    in_str = """
    Class Outer {
        a = 0;
        b = 1;
        
        Class Inner {
            a = 2;
            b = 3;

            def Inner(ai, bi){
                a = ai;
                b = bi;
            }
        }
    }
    print(Outer.Inner.a);    
    out_in = Outer.Inner(500, 99);
    print(out_in);

    out = Outer();
    in = out.Inner(7, 8);
    print(out);
    print(in);
    """
    
    ans_str = """
    2
    <Instance of Class: Inner, attrs: {'a': 500, 'b': 99, 'ai': 500, 'bi': 99} >
    <Instance of Class: Outer, attrs: {'a': 0, 'b': 1} >
    <Instance of Class: Inner, attrs: {'a': 7, 'b': 8, 'ai': 7, 'bi': 8} >
    """
    run_stdout_test(capfd, in_str, ans_str)