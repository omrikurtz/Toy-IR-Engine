from tokenize_utils import simpler_tokenization as tokenize


class Document(object):
    def __init__(self, doc_id, text):
        self._doc_id = doc_id
        self._text = text
        self._terms = self._parse_text()

    def _parse_text(self):
        return tokenize(self._text)

    @property
    def doc_id(self):
        return self._doc_id

    @property
    def text(self):
        return self._text

    @property
    def terms(self):
        return self._terms

    def __repr__(self):
        return "{id}: {text} ({terms})".format(id=self._doc_id, text=self._text, terms=self._terms)

    def __str__(self):
        return self._text
