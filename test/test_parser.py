import sys
sys.path.append('c:\\src\\lang-playground\\playground')

import pytest
from playground_parser import PlaygroundParser, ParsingError

class TestPlayGroundParser:
    def run_pg_parser(self, input_str):
        pgp = PlaygroundParser(input_str=input_str)
        pgp.testing = True 
        pgp.program()
        
    # Test that parsing fails with bad input 
    def test_add_expr1(self):
        with pytest.raises(ParsingError):
            self.run_pg_parser("5 + ")
            
    def test_add_expr2(self):
        with pytest.raises(ParsingError):
            self.run_pg_parser(" + 5")

    def test_add_expr3(self):
        with pytest.raises(ParsingError):
            self.run_pg_parser("+")

    def test_add_expr4(self):
        with pytest.raises(ParsingError):
            self.run_pg_parser("5 + 5")

    def test_add_expr5(self):
        with pytest.raises(ParsingError):
            self.run_pg_parser("5 + + ")

    def test_paren_expr1(self):
        with pytest.raises(ParsingError):
            self.run_pg_parser("(5 + )) * 3;")

    def test_paren_expr2(self):
        with pytest.raises(ParsingError):
            self.run_pg_parser("(5 + 3)) * 3;")
    
    # Test what parser should be able to parse 
    def test_can_parse(self):
        input_str = """
                5 + 5;
                10 + 10;
                5 - 5;
                5 * 5;
                5 / 5; 
                5 + 5 * 5;
                5 * 5 + 5;
                a * a - a;
                foo + foo * bar;
                (5 + 5) * foo;
                (5 + (5 + (5 + 5) + 5)) + 5;
                goo = 5;
                goo = bar;
                goo = 5 + 5;
                goo = (5 + 5);
                goo = (5 + 5) * 5;
                print(5);
                print(goo);
                print(5 + 5);
                print(a + a); 
                print(5 * (3 + 2));
                """
        try:
            self.run_pg_parser(input_str=input_str)
        except ParsingError:
            pytest.fail("Could not parse input")