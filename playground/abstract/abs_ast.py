class AST:
    def __init__(self, token=None, artificial=False, name=None):
        self.name = (
            name  # Artificial nodes won't have any "token_text", so give them a name
        )
        self.token = token  # From which token did we create node?
        self.children = []  # normalized list of AST nodes
        self.artificial = artificial

    def is_none(self):
        return self.token is None

    def add_child(self, t):
        self.children.append(t)

    def add_children(self, *children):
        for child in children:
            self.children.append(child)

    def __repr__(self):
        token = str(self.token) if self.token is not None else None
        artificial = self.name + " " if self.name is not None else None

        token_info = None
        if self.artificial:
            token_info = "ARTIFICIAL - " + artificial
        else:
            token_info = token
        ast_rep = f"<PG_AST: {token_info}>"
        return ast_rep

    def to_string_tree(self, tab=0):
        if len(self.children) == 0:
            print("| " * tab + str(self))
            return

        if not self.is_none():
            print("| " * tab + f"{self}")

        elif self.is_none() and self.artificial:
            print("| " * tab + f"{self}")

        for child in self.children:
            if child != None:
                child.to_string_tree(tab + 1)
