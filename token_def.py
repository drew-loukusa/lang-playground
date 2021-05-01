from enum import Enum, auto
class PlaygroundTokens(Enum):
    SEMI_COLON = auto()
    EQUAL = auto()
    LPAREN = auto()
    RPAREN = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    FSLASH = auto()
    NUMBER = auto()
    NAME = auto()
    INVALID_TOKEN_TYPE = 0
    EOF = -1 

class Token:
    def __init__(
            self, 
            token_type = PlaygroundTokens.INVALID_TOKEN_TYPE, 
            token_text = ""
        ):

        self.type = token_type
        self.text = token_text
    
    def __repr__(self):
        return "<" + str(self.type) + " '" + str(self.text) + "'>"

if __name__ == "__main__":
    for k,v in PlaygroundTokens.__members__.items():
        print(k,v, v.value)