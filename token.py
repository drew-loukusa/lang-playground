from enum import Enum, auto
class Tokens(Enum):
    PRINT = auto()    
    LPAREN = auto()
    RPAREN = auto()
    ADD_OP = auto()
    MULT_OP = auto()
    NUMBER = auto()
    INVALID_TOKEN_TYPE = 0
    EOF = -1 

class Token:
    def __init__(self, token_type = Tokens.INVALID_TOKEN_TYPE, token_text = ""):
        self.type = token_type
        self.text = token_text
    
    def __repr__(self):
        return "<Token: " + str(self.type) + " '" + str(self.text) + "'>"

if __name__ == "__main__":
    for k,v in Tokens.__members__.items():
        print(k,v, v.value)

    a = Token(Tokens.MULT_OP, "*")
    print(a)