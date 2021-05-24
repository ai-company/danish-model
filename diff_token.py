class DiffToken:
    def __init__(self, text, capitalization_mask, type, index, explanation, space=""):
        self.text = text
        self.capitalization_mask = capitalization_mask
        self.type = type
        self.index = index
        self.explanation = explanation
        self.space = space

    def __str__(self):
        return f'T<"{self.text}", {self.type} @ {self.index}>'

    def __repr__(self):
        return f'T<"{self.text}", {self.type} @ {self.index}>'
