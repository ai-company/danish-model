from copy import copy, deepcopy
from enum import Enum
from pprint import pprint
import re
from typing import List, Optional, Union


def tokenize(phrase, split_space=False):
    tokens: List[DiffToken] = []
    for i, token in enumerate(
        re.finditer(
            r"(?P<NUMB>[0-9]+([,.][0-9]+)*)|(?P<WORD>\w+)|(?P<SPAC>\t|\n|\s+)|(?P<PUNC>\W)",
            phrase,
        )
    ):
        type = LexemeType[
            list({k: v for k, v in token.groupdict().items() if v is not None}.keys())[
                0
            ]
        ]

        if type == LexemeType.SPAC:
            tokens[-1].lexeme.space = token.group(0)
        else:
            tokens.append(DiffToken(Lexeme(token.group(0), type), None))

    for i, token in enumerate(tokens):
        token.index = i

    return tokens


class LexemeType(Enum):
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


class Lexeme:
    def __init__(
        self,
        text,
        type,
        space="",
        pos=None,
        spacy=None,
    ):
        self.text = text
        self.type = type
        self.space = space
        self.pos_ = pos
        self.spacy = spacy

    def __str__(self):
        return f"{self.text}{self.space}"

    def __repr__(self):
        return f'"{self.text}{self.space}"{" " + self.pos_ if self.pos_ else ""}'


class DiffToken:
    def __init__(
        self,
        lexeme: Lexeme,
        index: Union[int, List[int], None],
        explanation=[],
        origin=None,
        change_type="none",
        change=None,
    ):
        self.lexeme = lexeme
        self.index = index
        self.explanation = explanation
        self.origin = origin
        self.change_type = change_type
        self.change = change

    @classmethod
    def from_spacy_list(cls, tokens):
        canon = []

        i = 0
        for token in tokens:
            if token.pos_ == "SPACE":
                canon[-1].lexeme.space += token.text
            else:
                canon.append(
                    cls(
                        Lexeme(
                            token.text,
                            LexemeType.from_pos(token.pos_),
                            token.whitespace_,
                            token.pos_,
                            token,
                        ),
                        i,
                        [],
                    )
                )
                i += 1

        return canon

    def to_dict(self) -> dict:
        result = {
            "type": self.change_type,
            "origin": str(self.lexeme)
            if self.origin is None
            else list(map(str, self.origin)),
        }

        if len(self.explanation) > 0:
            result["explain"] = self.explanation

        if self.change:
            result["change"] = (
                self.change
                if type(self.change) is not list
                else list(map(DiffToken.to_dict, self.change))
            )

        return result

    @classmethod
    def from_dict(cls, dict: dict, index: Union[int, List[int], None] = None):
        lexeme = []

        if "origin" in dict:
            if type(dict["origin"]) == str:
                lexeme = tokenize(dict["origin"])[0].lexeme
            else:
                lexeme = tokenize("".join(dict["origin"]))[0].lexeme

        changes = []

        if "change" in dict:
            if type(dict["change"]) == str:
                changes = dict["change"]
                lexeme = tokenize(changes)[0].lexeme
            else:
                changes = list(map(DiffToken.from_dict, dict["change"]))
                lexeme = tokenize(
                    "".join(map(lambda c: c.get("change", c["origin"]), dict["change"]))
                )[0].lexeme
        else:
            changes = None

        return cls(
            lexeme,
            index,
            dict.get("explain", []),
            dict.get("origin"),
            dict["type"],
            changes,
        )

    def clone(self):
        token = copy(self)
        token.lexeme = copy(self.lexeme)
        token.explanation = copy(self.explanation)
        return token

    def clone_clean(self):
        token = copy(self)
        token.lexeme = copy(self.lexeme)
        token.explanation = []
        token.change_type = "none"
        token.change = None
        return token

    def strip(self) -> str:
        space = self.lexeme.space
        self.lexeme.space = ""
        return space

    def stripped(self):
        token = copy(self)
        token.lexeme = copy(self.lexeme)
        token.explanation = copy(self.explanation)
        token.lexeme.space = ""
        return token

    def __str__(self):
        return str(self.lexeme)

    def __repr__(self):
        explanation = f" {self.explanation}" if len(self.explanation) > 0 else ""
        change_type = f" {self.change_type}" if self.change_type != "none" else ""
        change = f": '{self.change}'" if self.change else ""

        return "{:>3}: {}{}{}{}".format(
            str(self.index) if self.index is not None else "+++",
            repr(self.lexeme),
            explanation,
            change_type,
            change,
        )


class DiffWord(DiffToken):
    def __init__(
        self,
        text,
        index,
        explanation=[],
        space="",
        pos=None,
        origin=None,
        change_type="none",
        change=None,
    ):
        super().__init__(
            Lexeme(text, LexemeType.WORD, space, pos),
            index,
            explanation,
            origin,
            change_type,
            change,
        )


class DiffPunc(DiffToken):
    def __init__(
        self,
        text,
        index,
        explanation=[],
        space="",
        origin=None,
        change_type="none",
        change=None,
    ):
        super().__init__(
            Lexeme(text, LexemeType.PUNC, space, "PUNCT"),
            index,
            explanation,
            origin,
            change_type,
            change,
        )


class DiffSpac(DiffToken):
    def __init__(self, text, index):
        super().__init__(
            Lexeme(text, LexemeType.SPAC, text, "SPACE"), index, [], None, "space"
        )


class DiffNumb(DiffToken):
    def __init__(
        self,
        text,
        index,
        explanation=[],
        space="",
        origin=None,
        change_type="none",
        change=None,
    ):
        super().__init__(
            Lexeme(text, LexemeType.NUMB, space, "NUM"),
            index,
            explanation,
            origin,
            change_type,
            change,
        )
