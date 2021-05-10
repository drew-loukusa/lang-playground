from base.abstract_syntax_tree import AST

class PG_AST(AST):
    def __init__(self, token=None, artificial=False, name=None):
        super().__init__(token=token, artificial=artificial, name=name)