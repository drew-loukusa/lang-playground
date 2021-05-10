class AbstractToken:
    def __init__(
            self, 
            token_type = None, 
            token_text = ""
        ):

        self.type = token_type
        self.text = token_text
    
    def __repr__(self):
        return "<" + str(self.type) + " '" + str(self.text) + "'>"