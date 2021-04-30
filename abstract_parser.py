class Parser:
    def __init__(self, input_lexer, k=1):
        self.input = input_lexer
        self.k = k              # How many lookahead tokens
        self.p = 0              # Circular index of next token positon to fill
        self.lookahead = []     # Circular lookahead buffer 
        for _ in range(k):      # Prime buffer
            self.lookahead.append(self.input.next_token())

    def consume(self):
        self.lookahead[self.p] = self.input.next_token()
        self.p = (self.p+1) % self.k 

    def LT(self, i):         
        return self.lookahead[(self.p + i - 1) % self.k] # Circular fetch
    
    def LA(self, i): return self.LT(i).type 

    def match(self, x):
        """ Accepts token type as a Tokens enum attribute """
        if self.LA(1) == x: # x is token_type 
            self.consume()
        else:
            raise Exception(f"Expecting {self.input.getTokenName(x)}; found {self.LT(1)}")            
    
    # Lookahead sequence is:
    def LA_SEQ_IS(self, *token_type_sequence):
        """ Sequentially checks if the lookahead tokens match a given sequence."""
        if len(token_type_sequence) > self.k: 
            msg = "Length of token sequence to be checked greater than the lookahead"
            msg += "set for this parser. Increase this parsers k value, or modify this token sequence length."
            msg += f"Current k value: {self.k}, Token Type Sequence: {token_type_sequence}"
            raise Exception()
        for i, token_type in enumerate(token_type_sequence):
            if not self.LA(i) == token_type:
                return False 
        return True 