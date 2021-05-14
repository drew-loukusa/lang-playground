import sys
sys.path.append('c:\\src\\lang-playground\\playground')

import pytest
from playground_interpreter import PlaygroundInterpreter

def run_stdout_test(capfd, in_str, ans_str):
    pgp = PlaygroundInterpreter()
    pgp.interp(input_str=in_str)
    out, err = capfd.readouterr()
    assert out.rstrip() == ans_str

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
    in_str="""
    a = 10;
    {
        print(a);
        a = 5;
    }
    """
    run_stdout_test(capfd, in_str, "10")

def test_nested_2(capfd):
    in_str="""
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
    in_str = "if(False){print(\"False\");}else{print(\"True\");}"
    ans_str = "True"
    run_stdout_test(capfd, in_str, ans_str)

def test_cond_3(capfd):
    in_str = "if(False){print(\"False\");}elif(True){print(\"True\");}"
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


