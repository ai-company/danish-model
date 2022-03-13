from copy import copy, deepcopy
from enum import Enum
from pprint import pprint
from typing import List, Optional, Union

import re


def tokenize(phrase, split_space=False):
    tokens: List[DiffToken] = []
    for i, token in enumerate(
        re.finditer(
            r"(?P<NUMB>[0-9]+([,.][0-9]+)*)|(?P<WORD>\w+)|(?P<SPAC>\t|\n|\s+)|(?P<PUNC>\W)",
            phrase,
        )
    ):
        lexeme_type = LexemeType[
            list({k: v for k, v in token.groupdict().items() if v is not None}.keys())[
                0
            ]
        ]

        if lexeme_type == LexemeType.SPAC:
            if len(tokens) > 0:
                tokens[-1].lexeme.space += token.group(0)
                tokens[-1].origin += token.group(0)
            else:
                tokens.append(DiffSpac(token.group(0), None))
        elif lexeme_type == LexemeType.PUNC:
            tokens.append(DiffPunc(token.group(0), None, origin=token.group(0)))
        elif lexeme_type == LexemeType.NUMB:
            tokens.append(DiffNumb(token.group(0), None, origin=token.group(0)))
        else:
            tokens.append(DiffWord(token.group(0), None, origin=token.group(0)))

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

    @classmethod
    def from_text(cls, text):
        return tokenize(text)[0].lexeme.type


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
        return f'"{self.text}{self.space}"{" " + str(self.type) + ":" + (self.pos_ if self.pos_ else "")}'

    @classmethod
    def from_str(cls, source) -> "Lexeme":
        tokens = tokenize(source)

        text = None
        space = None

        if tokens[0].lexeme.type != LexemeType.SPAC:
            text = source[: len(source.strip())]
            space = source[len(source.strip()) :]
        else:
            text = source
            space = ""

        non_punct = list(
            filter(
                lambda t: t.lexeme.type in (LexemeType.WORD, LexemeType.NUMB), tokens
            )
        )

        ltype = tokens[0].lexeme.type
        pos = tokens[0].lexeme.pos_

        if len(non_punct) > 0:
            ltype = non_punct[0].lexeme.type
            pos = non_punct[0].lexeme.pos_

        return cls(text, ltype, space, pos)


class DiffToken:
    def __init__(
        self,
        lexeme: Lexeme,
        index: Union[int, List[int], None],
        explanation: Union[str, List[str]] = [],
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
    def from_spacy_list(cls, spacy, flatten=True) -> List["DiffToken"]:
        tokens = []

        i = 0
        for token in spacy:
            if token.pos_ == "SPACE":
                if len(tokens) > 0:
                    tokens[-1].lexeme.space += token.text
                    tokens[-1].origin += token.text
                else:
                    tokens.append(DiffSpac(token.text, i))
                    i += 1
            else:
                tokens.append(
                    cls(
                        Lexeme(
                            token.text,
                            LexemeType.from_text(token.text),
                            token.whitespace_,
                            token.pos_,
                            token,
                        ),
                        i,
                        [],
                        token.text + token.whitespace_,
                    )
                )
                i += 1

        if flatten:
            return cls.flatten(tokens)
        else:
            return tokens

    @classmethod
    def flatten(cls, tokens: List["DiffToken"]) -> List["DiffToken"]:
        # spacy sometimes produces garbage token merges, so we have to flatten these out
        flattened = []
        # doesn't start with number, is alphanumeric, has dash, single quote or space
        normal_word = re.compile(r"^(?!\d+)[\w\-'’‘‛ ]+$")
        for token in tokens:
            if (
                token.lexeme.type == LexemeType.PUNC
                or normal_word.match(str(token.lexeme)) is None
            ):
                new_tokens = tokenize(str(token.lexeme))
                non_punct = list(
                    filter(
                        lambda t: t.lexeme.type in (LexemeType.WORD, LexemeType.NUMB),
                        new_tokens,
                    )
                )
                if (
                    len(non_punct) > 0
                    and normal_word.match(str(token.lexeme)) is not None
                ):
                    token.lexeme.type = non_punct[0].lexeme.type
                    token.lexeme.pos_ = non_punct[0].lexeme.pos_
                    flattened.append(token)
                else:
                    flattened.extend(new_tokens)
            else:
                flattened.append(token)

        for i, token in enumerate(flattened):
            token.index = i

        return flattened

    def to_dict(self) -> dict:
        result = {
            "type": self.change_type,
        }

        if self.origin is not None:
            result["origin"] = (
                self.origin
                if type(self.origin) is not list
                else list(map(str, self.origin))
            )

        if len(self.explanation) > 0:
            result["explain"] = (
                self.explanation
                if type(self.explanation) is list
                else [self.explanation]
            )

        if self.change is not None:
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
                lexeme = Lexeme.from_str(dict["origin"])
            else:
                lexeme = Lexeme.from_str("".join(dict["origin"]))

        changes = []

        if "change" in dict:
            if type(dict["change"]) == str:
                changes = dict["change"]
                lexeme = Lexeme.from_str(changes)
            else:
                changes = list(map(DiffToken.from_dict, dict["change"]))
                lexeme = Lexeme.from_str(
                    "".join(
                        map(
                            lambda c: c.get("change", c.get("origin", "")),
                            dict["change"],
                        )
                    )
                )
        else:
            changes = None

        explain = dict.get("explain", [])

        return cls(
            lexeme,
            index,
            explain if type(explain) is list else [explain],
            dict.get("origin"),
            dict["type"],
            changes,
        )

    def clone(self):
        token = copy(self)
        token.lexeme = copy(self.lexeme)
        token.explanation = copy(self.explanation)
        token.origin = copy(self.origin)
        token.change = copy(self.change)
        return token

    def clone_clean(self):
        token = copy(self)
        token.lexeme = copy(self.lexeme)
        token.explanation = []
        token.origin = str(self.lexeme)
        token.change_type = "none"
        token.change = None
        return token

    def strip(self) -> str:
        space = self.lexeme.space
        self.lexeme.space = ""
        if self.change is not None:
            self.change = self.change.strip()
        return space

    def stripped(self):
        token = copy(self)
        token.lexeme = copy(self.lexeme)
        token.lexeme.space = ""
        token.explanation = copy(self.explanation)

        token.origin = copy(self.origin)
        if type(token.origin) is str:
            token.origin = token.origin.strip()
        elif type(token.origin) is list:
            token.origin[-1] = str(token.origin[-1]).strip()

        token.change = copy(self.change)
        if type(token.change) is str:
            token.change = token.change.strip()

        return token

    def __str__(self):
        return str(self.lexeme)

    def __repr__(self):
        explanation = f" {self.explanation}" if len(self.explanation) > 0 else ""
        change_type = f" {self.change_type}" if self.change_type != "none" else ""
        change = f": '{self.change}'" if self.change else ""
        origin = (
            f" from: '{self.origin}'"
            if self.origin is not None and self.origin != str(self.lexeme)
            else ""
        )

        return "{:>3}: {}{}{}{}{}".format(
            str(self.index) if self.index is not None else "+++",
            repr(self.lexeme),
            explanation,
            origin,
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
            Lexeme(text, LexemeType.SPAC, "", "SPACE"), index, [], text, "space"
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
