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
        return f"<Function: {self.name}, params: {self.params} >"

class PG_Class(PG_Scope):
    def __init__(self, name: str, is_class_def=False):
        # Is this the "original" object? I.E. the class definition?
        self.is_class_def = is_class_def
        super().__init__(name=name)
        self.methods = defaultdict(dict)
    
    def __repr__(self):
        return f"< Class: {self.name}, attrs: {self.attrs} methods: {self.methods} >"