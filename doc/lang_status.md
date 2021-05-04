Just wanted to start a doc to track the general, high level status of this project.

Currently using a hand-built everything, lexer, parser, AST contstructer and high level interpreter.

# Lexer

The lexer is a fairly straight forward lexer. It scans the input string one char at a time and builds tokens as needed. Numbers and Names which are multi-character tokens call the consume() method as many times as is needed to build said tokens.

I currently only have a single reserved word: 'print', which I have given it's own token type.

I'm not sure if I want to handle reserved words in the lexer though.
I'll need to look at other language implementations and see how they do it before I make my decision.

If I do move forward with giving each reserved word it's own token type, the way I'm handeling that is by using a dict of 'reversed_word' -> token_type' in the lexer to check after lexing a NAME if said NAME is a reserved word, and if yes, then return a token of that type instead of NAME.

# Parser 
It's a hand built LL(2) (two tokens of lookahead) parser. Nothing special. If more tokens of look ahead are needed, it's _very_ easy to increase the amount of lookahead; literally change an integer argument.

The parser accepts the input string as input, and returns an AST of type PG_AST.

# Typing

I'm leaning on Python's type system to do most of the lifting for me. I can parse ints (of any size) and floats, and then I just pass them off to Python to do type promotion, and operations.