# A small package that will include tokenizing functions. We can import whatever tokenizing function we want from here
import string

from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


def simple_tokenization(text):
    """
    Parses text (string) and returns words after tokenizing it.
    :param text: A string represents the document text.
    :return: A tokenized list of strings (the words).
    """
    words = word_tokenize(text)
    return [word.lower() for word in words if word not in stopwords.words("english")]


def simpler_tokenization(text):
    words = text.translate(None, string.punctuation).split()
    terms = []
    for word in words:
        word = unicode(word, 'utf-8', errors='ignore').strip()
        word = word.encode('ascii', 'ignore').lower()
        if word not in stopwords.words("english"):
            terms.append(word)
    return terms


def smart_tokenizer(text):
    """
    Another tokenization function that uses stemming, but is slower than simple/simpler.
    :param text: The input text.
    :return: Tokenized, stemmed words from input text (List of strings)
    """
    words = text.translate(None, string.punctuation).split()
    stemmer = PorterStemmer()
    return [stemmer.stem(word.lower()) for word in words if word not in stopwords.words("english")]
