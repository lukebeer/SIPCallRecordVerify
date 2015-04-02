__author__ = 'luke Berezynskyj <eat.lemons@gmail.com>'


import logging
import nltk.corpus
import nltk.tokenize.punkt
import nltk.stem.snowball
import string


class Verify:

    def __init__(self, threshold=0.5):
        self.threshold = threshold

    def setup(self):
        try:
            self.stopwords = nltk.corpus.stopwords.words('english')
            self.stopwords.extend(string.punctuation)
            self.tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer()
            self.stemmer = nltk.stem.snowball.SnowballStemmer('english')
            return True
        except LookupError:
            nltk.download()
            if not self.setup():
                logging.error("Error downloading nltk")
        return False

    def verify(self, compare_this, against_this):
        if not self.setup():
            return False
        tokens_a = [token.lower().strip(string.punctuation) for token in self.tokenizer.tokenize(compare_this) \
                    if token.lower().strip(string.punctuation) not in self.stopwords]
        tokens_b = [token.lower().strip(string.punctuation) for token in self.tokenizer.tokenize(against_this) \
                    if token.lower().strip(string.punctuation) not in self.stopwords]
        stems_a = [self.stemmer.stem(token) for token in tokens_a]
        stems_b = [self.stemmer.stem(token) for token in tokens_b]

        ratio = len(set(stems_a).intersection(stems_b)) / float(len(set(stems_a).union(stems_b)))
        return (ratio >= self.threshold)