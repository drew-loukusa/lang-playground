from enum import Enum, auto
class Token(Enum):
    PRINT = auto()    
    LPAREN = auto()
    RPAREN = auto()
    ADD_OP = auto()
    MULT_OP = auto()
    NUMBER = auto()
    INVALID_TOKEN_TYPE = 0
    EOF = -1 

if __name__ == "__main__":
    for k,v in Token.__members__.items():
        print(k,v, v.value)

