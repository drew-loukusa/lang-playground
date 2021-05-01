from token_def import AbstractToken

class AST:

    def __init__(self, token=None, artificial=False, name=None):
        self.name = name    # Artificial nodes won't have any "token_text", so give them a name 
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

    def to_string(self):
        foo = str(self.token) if self.token is not None else "None"
        foo = self.name + str(self.token) if self.name is not None else foo 

        if self.artificial: 
            foo = 'ARTIFICIAL - ' + foo 

        return foo

    def to_string_tree(self, tab=0):
        if len(self.children) == 0: 
            print('| '*tab + self.to_string())
            return

        if not self.is_none(): 
            print('| '*tab + f"{self.to_string()}")

        elif self.is_none() and self.artificial:
            print('| '*tab + f"{self.to_string()}")
        
        for child in self.children:
            child.to_string_tree(tab+1)