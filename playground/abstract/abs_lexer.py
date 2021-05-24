class AbstractLexer:
    def __init__(self, input_str):
        self.EOF = chr(0)
        self.EOF_TYPE = -1

        self.input = input_str
        self.p = 0
        self.c = self.input[self.p]

        self.line_number = 0

    def consume(self) -> str:
        """
        Increments self.c to the next to the next char in the input string.
        Returns value of self.c before it was incremented
        """
        c = self.c
        self.p += 1
        if self.p >= len(self.input):
            self.c = self.EOF
        else:
            self.c = self.input[self.p]
        return c

    def rewind(self, n: int):
        """
        Rewinds the character stream by 'n' characters.
        Sets self.p = self.p - n
        Then, sets self.c = self.p
        """
        self.p = self.p - n
        self.c = self.input[self.p]

    def _WS(self):
        """
        Consumes whitespace until a non-whitespace char is encountered.
        """
        while self.c in [" ", "\t", "\n", "\r"]:
            if self.c == "\n":
                self.line_number += 1
            self.consume()

    def _comment(self):
        """
        Skips comments, lines that start with a '#', by consuming chars until a new line is encountered.
        """
        while self.c != "\n":
            self.consume()  # Consume the comment,
