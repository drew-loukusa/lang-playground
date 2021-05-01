from abstract_syntax_tree import AST

class ParsingError(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)

class AbstractParser:
    def __init__(self, input_lexer, k=1):
        self.input = input_lexer # A lexer with method nextToken() defined
        self.k = k              # How many lookahead tokens
        self.p = 0              # Circular index of next token positon to fill
        self.lookahead = []     # Circular lookahead buffer 
        for _ in range(k):      # Prime buffer
            self.lookahead.append(self.input.next_token())

    def consume(self):
        """ Increments the lookahead token buffer by 1 token """
        self.lookahead[self.p] = self.input.next_token()
        self.p = (self.p+1) % self.k 

    def LT(self, i):     
        """ Returns the i'th lookahead token """    
        return self.lookahead[(self.p + i - 1) % self.k] # Circular fetch
    
    def LA(self, i): 
        """ Returns type of the i'th lookahead token """ 
        return self.LT(i).type 

    def match(self, x):
        """ Accepts token type as a Tokens enum attribute 
            Returns an AST node """
        if self.LA(1) == x: # x is token_type 
            node = AST(self.LT(1))
            self.consume()
            return node 
        else:
            raise ParsingError(f"Expecting {x}; found {self.LT(1)} on line {self.input.line_number}")