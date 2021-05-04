from enum import Enum, auto
from base.abstract_token import AbstractToken 
class PG_Type(Enum):
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
    PRINT = auto()
    INVALID_TOKEN_TYPE = 0
    EOF = -1 

class PG_Token(AbstractToken):
    def __init__(self, token_type=None, token_text=''):
        super().__init__(token_type=token_type, token_text=token_text)
        self.scope = "global"

if __name__ == "__main__":
    for k,v in PG_Type.__members__.items():
        print(k,v, v.value)