from copy import copy
from enum import Enum


class DiffTokenType(Enum):
    WORD = "WORD"
    PUNC = "PUNC"
    SPAC = "SPAC"
    NUMB = "NUMB"

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_pos(cls, pos):
        posmap = {
            "NUM": cls.NUMB,
            "PUNCT": cls.PUNC,
            "SPACE": cls.SPAC,
        }

        return posmap[pos] if pos in posmap else cls.WORD


class DiffToken:
    def __init__(
        self, text, capitalization_mask, type, index, explanation=[], space="", pos="?"
    ):
        self.text = text
        self.capitalization_mask = capitalization_mask
        self.type = type
        self.index = index
        self.explanation = explanation
        self.space = space
        self.pos_ = pos

    def strip(self):
        space = self.space
        self.space = ""
        return space

    def stripped(self):
        token = copy(self)
        token.space = ""
        return token

    def __str__(self):
        return f'{self.index}: {self.type}"{self.text}{self.space}"'

    def __repr__(self):
        return f'{self.index}: {self.type}"{self.text}{self.space}"'


class DiffWord(DiffToken):
    def __init__(self, text, index, explanation=[], space="", pos="?"):
        super().__init__(text, text, DiffTokenType.WORD, index, explanation, space, pos)


class DiffPunc(DiffToken):
    def __init__(self, text, index, explanation=[], space=""):
        super().__init__(
            text, text, DiffTokenType.PUNC, index, explanation, space, "PUNCT"
        )


class DiffSpac(DiffToken):
    def __init__(self, text, index):
        super().__init__(text, text, DiffTokenType.SPAC, index, text, "SPACE")


class DiffNumb(DiffToken):
    def __init__(self, text, index, explanation=[], space=""):
        super().__init__(
            text, text, DiffTokenType.NUMB, index, explanation, space, "NUM"
        )
