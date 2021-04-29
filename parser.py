class Parser:
    def __init__(self, input_lexer, k=1):
        self.input = input_lexer
        self.k = k              # How many lookahead tokens
        self.p = 0              # Circular index of next token positon to fill
        self.lookahead = []     # Circular lookahead buffer 
        for _ in range(k):      # Prime buffer
            self.lookahead.append(self.input.nextToken())

    def consume(self):
        self.lookahead[self.p] = self.input.nextToken()
        self.p = (self.p+1) % self.k 

    def LT(self, i):         
        return self.lookahead[(self.p + i - 1) % self.k] # Circular fetch
    
    def LA(self, i): return self.LT(i).type 

    def match(self, x):
        """ Accepts token type as a Tokens enum attribute """
        if self.LA(1) == x: # x is token_type 
            self.consume()
        else:
            raise Exception(f"Expecting {self.input.getTokenName(x)}; found {self.LT(1)} on line # {self.LT(1)._line_number}")            