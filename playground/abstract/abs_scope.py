class AbstractScope:
    def __init__(self, name=None):
        self.name = name 
        self.depth = 0
        self.symbols: dict = {}
        self.parent: Scope = None 
        self.children: list[Scope, ...] = []
    
    def __repr__(self):
        return f"< Scope: {self.name}, depth: {self.depth}, parent: {self.parent.name}, num_children {len(self.children)}"

    def resolve(self, symbol: str):
        """ 
           Attempts to locate and return whatever value was assigned to 
           'symbol' if 'symbol' exists in the current scope, or any 
           parent scope.
        """
        cur_scope = self 
        while cur_scope != None:
            if symbol in cur_scope.symbols:
                return cur_scope.symbols[symbol]
            cur_scope = cur_scope.parent 
        raise NameError(f"Symbol {symbol} could not be found!")

    def resolve_scope(self, symbol: str):
        """ 
           Attempts to locate and return the scope object of symbol
           'symbol' if 'symbol' exists in the current scope, or any 
           parent scope.
        """
        cur_scope = self 
        while cur_scope != None:
            if symbol in cur_scope.symbols:
                return cur_scope
            cur_scope = cur_scope.parent 
        return None