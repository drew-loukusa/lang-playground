from collections import defaultdict

from playground_ast import PG_AST
from abstract.abs_scope import AbstractScope


class PG_Scope(AbstractScope):
    def __init__(self, name=None):
        super().__init__(name=name)


class PG_Function:
    def __init__(self, name: str, params: PG_Scope, code: PG_AST):
        self.name = name
        self.params = params
        self.code = code

    def __repr__(self):
        return f"<Function: {self.name}, params: {self.params}>"


class PG_Class(PG_Scope):
    def __init__(self, name: str, is_class_def=False):
        # Is this the "original" object? I.E. the class definition?
        self.is_class_def = is_class_def
        super().__init__(name=name)
    
    def _is_func_dict(self, item):
        return (
            type(item) is dict 
            and type(list(item.keys())[0]) is int 
            and type(list(item.values())[0]) is PG_Function
        )

    @property
    def attrs(self):
        return { k:v for k,v in self.symbols.items() if not self._is_func_dict(v) }
        
    @property
    def methods(self):
        return { k:v for k,v in self.symbols.items() if self._is_func_dict(v) }

    def __repr__(self):
        if self.is_class_def:
            return f"<Class Definition: {self.name}, attrs: {self.attrs} >"
        return f"<Instance of Class: {self.name}, attrs: {self.attrs} >"

if __name__ == "__main__":
    foo = PG_Class(name="FooClass")
    foo.symbols['a'] = 10 
    foo.symbols['b'] = 20
    foo.symbols['func1'] = { 0: PG_Function(name="func1", params=None, code=None) }
    foo.symbols['func2'] = { 1: PG_Function(name="func2", params=None, code=None) }

    # for k,v in foo.symbols.items():
    #     print(k,v)
    print("ATTRS:")
    print("===============")
    print(foo.attrs)

    print("\nMETHODS:")
    print("===============")
    print(foo.methods)