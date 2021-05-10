class Symbol:
    def __init__(self, name, symbol_type=None):
        self.name = name 
        self.type = symbol_type 
    
    def __repr__(self):
        return f"<{self.name}:{self.type}>"

class VariableSymbol(Symbol):
    def __init__(self, name, symbol_type=None):
        super().__init__(name, symbol_type)


class Scope:

    def get_scope_name(self) -> str:
        pass
   
    def get_enclosing_scope(self):
        """ Returns a Scope object """
        pass
   
    def define(self, sym: Symbol):
        pass
   
    def resolve(self, name: str) -> Symbol:
        pass

class SymbolTable(Scope):
    def __init__(self):
        super().__init__()
        self.symbols = {} # str -> Symbol

    def __repr__(self):
        return self.get_scope_name() + ":" + self.symbols

    def init_type_system(self):
        pass

    def get_scope_name(self):
        return "global"

    def get_enclosing_scope(self):
        return None 

    def define(self, sym: Symbol):
        self.symbols[sym.name] = sym

    def resolve(self, name: str) -> Symbol:
        return self.symbols[name]

    