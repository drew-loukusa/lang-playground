class Lexer:
    def __init__(self, input_str):
        self.EOF = chr(0)
        self.EOF_TYPE = 1 

        self.input = input_str
        self.p = 0
        self.c = self.input[self.p]

    def consume(self):
        """ Increments the char pointer int 'p' by one and sets 
            'c' to the next char in the input string """
        self.p += 1
        if self.p >= len(self.input):
            self.c = self.EOF 
        else: 
            self.c = self.input[self.p]

    def _WS(self):
        """ Consumes whitespace until a non-whitespace char is encountered. """
        while self.c in [' ','\t','\n','\r']: 
            self.consume()
    
    def _comment(self):
        """ Skips comments, lines that start with a '#', by consuming chars until a new line is encountered. """
        while self.c != '\n': 
            self.consume()      # Consume the comment,   