import nltk
from nltk.util import trigrams
from nltk.util import bigrams
import sys
import os
import os.path
import string


class Pythonsky(object):
    PARAGRAPH_DELIMITER = "\n\n"
    TEXT_DELIMITER = "\n\n"
    SPEACH_DELIMITER = "\"'"
    SENTANCE_END = "?!.'"

    def __init__(self, wdir):
        self._text = ""

        for text_file_name in os.listdir(wdir):
            text_file = file(os.path.join(wdir, text_file_name))
            if not os.path.isfile(os.path.join(wdir, text_file_name)):
                continue
            self._text += text_file.read().decode(
                'utf8') + Pythonsky.TEXT_DELIMITER

        tokens = self._tokenize()
        self._trigram_pd = nltk.ConditionalProbDist(
            nltk.ConditionalFreqDist(
                [(t[:2], t[2]) for t in trigrams(tokens)]),
            nltk.probability.ELEProbDist)

        self._bigram_pd = nltk.ConditionalProbDist(
            nltk.ConditionalFreqDist([(t[:1], t[1]) for t in bigrams(tokens)]),
            nltk.probability.ELEProbDist)

        self._sent_tokenizer = nltk.tokenize.PunktSentenceTokenizer(
            self._text)

        sentances = self._sent_tokenizer.tokenize(self._text)

        self._sent_begin_pd = nltk.ELEProbDist(
            nltk.FreqDist(
                [nltk.word_tokenize(t)[0]
                 for t in sentances]))

        self._paragraph_length_pd = nltk.ELEProbDist(
            nltk.FreqDist(
                [len(self._sent_tokenizer.tokenize(t)) for t in
                 nltk.blankline_tokenize(self._text)]))

    def _tokenize(self):
        return nltk.word_tokenize(self._text)

    def _sentance_first_word(self):
        return self._sent_begin_pd.generate()

    def _sentance_second_word(self, first_word):
        return self._bigram_pd[(first_word, )].generate()

    def _sequent_word(self, previous_word, word_before_previous):
        return self._trigram_pd[(
            word_before_previous, previous_word)].generate()

    def _setntance_end(self):
        return self._sent_end_pd.generate()

    def _wrap_with_space(self, word):
        if word[0] not in string.punctuation:
            return " " + word
        else:
            return word

    def _sentance(self):
        first_word = self._sentance_first_word()
        while first_word in Pythonsky.SENTANCE_END:
            first_word = self._sentance_first_word()

        second_word = self._sentance_second_word(first_word)

        previous_word = second_word
        word_before_previous = first_word
        sent = [first_word, second_word]
        while previous_word not in Pythonsky.SENTANCE_END:
            sequent_word = self._sequent_word(
                previous_word, word_before_previous)
            sent.append(sequent_word)

            word_before_previous = previous_word
            previous_word = sequent_word

        sent = "".join(map(self._wrap_with_space, sent))
        if sent[0] in Pythonsky.SPEACH_DELIMITER and sent[-1] not in Pythonsky.SPEACH_DELIMITER:
           sent += sent[0]

        if sent[-1] in Pythonsky.SPEACH_DELIMITER and sent[0] not in Pythonsky.SPEACH_DELIMITER:
           sent = sent[-1] + sent

        return sent

    def _paragraph(self):
        length = self._paragraph_length_pd.generate()

        assert length > 0
        sents = []
        while length > 0:
            sents.append(self._sentance())
            length -= 1

        return " ".join(sents)[1:]

    def make_text_of_expected_length(self, length=1000):
        text = ""

        while len(text) < length:
            text += self._paragraph() + Pythonsky.PARAGRAPH_DELIMITER

        return text


if __name__ == "__main__":
    print Pythonsky(
        './test').make_text_of_expected_length(int(sys.argv[1]))
