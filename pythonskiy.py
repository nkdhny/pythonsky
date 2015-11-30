import nltk
from nltk.util import trigrams
from nltk.util import bigrams
import sys
import os
import os.path
import string
import pickle


class Pythonsky(object):
    PARAGRAPH_DELIMITER = "\n\n"
    SPEACH_DELIMITER = "\"'"
    SENTENCE_END = "?!."

    def __init__(self, work_dir):
        self._text = ""

        tokens = []
        sentences = []
        paragraphs = []
        paragraph_sentence_length = []
        first_word = []

        for path_to_text, _, text_file_names in os.walk(work_dir):
            for text_file_name in text_file_names:
                text_file = file(
                    os.path.join(path_to_text, text_file_name))

                if not os.path.isfile(
                     os.path.join(path_to_text, text_file_name)):
                    continue
                file_content = text_file.read().decode('utf8')
                print text_file_name

                text_paragraphs = nltk.blankline_tokenize(file_content)
                paragraphs += text_paragraphs

                self._sent_tokenizer = nltk.tokenize.PunktSentenceTokenizer(
                    file_content)

                for paragraph in text_paragraphs:
                    paragraph_sentence = self._sent_tokenizer.tokenize(
                        paragraph)
                    paragraph_sentence_length.append(len(paragraph_sentence))
                    sentences += paragraph_sentence
                    for sentence in paragraph_sentence:
                        sentence_tokens = nltk.word_tokenize(sentence)
                        tokens += sentence_tokens
                        first_word.append(sentence_tokens[0])

        self._trigram_pd = nltk.ConditionalProbDist(
            nltk.ConditionalFreqDist(
                [(t[:2], t[2]) for t in trigrams(tokens)]),
            nltk.probability.ELEProbDist)

        self._bigram_pd = nltk.ConditionalProbDist(
            nltk.ConditionalFreqDist([(t[:1], t[1]) for t in bigrams(tokens)]),
            nltk.probability.ELEProbDist)

        self._sent_begin_pd = nltk.ELEProbDist(
            nltk.FreqDist(first_word))

        self._paragraph_length_pd = nltk.ELEProbDist(
            nltk.FreqDist(paragraph_sentence_length))

    def _tokenize(self):
        return nltk.word_tokenize(self._text)

    def _sentence_first_word(self):
        return self._sent_begin_pd.generate()

    def _sentence_second_word(self, first_word):
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

    def _sentence(self):
        first_word = self._sentence_first_word()
        while first_word in Pythonsky.SENTENCE_END:
            first_word = self._sentence_first_word()

        second_word = self._sentence_second_word(first_word)

        previous_word = second_word
        word_before_previous = first_word
        sent = [first_word, second_word]
        while previous_word not in Pythonsky.SENTENCE_END:
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
            sents.append(self._sentence())
            length -= 1

        return " ".join(sents)[1:]

    def make_text_of_expected_length(self, length=1000):
        text = ""

        while len(text) < length:
            text += self._paragraph() + Pythonsky.PARAGRAPH_DELIMITER

        return text


def usage():
    print "train|cmpose"
    print "train (corpus dir) (output path)"
    print "compose (trained pythonsky) (text length)"

if __name__ == "__main__":
    if len(sys.argv) < 4:
        usage()
        exit(0)
    if sys.argv[1] == 'train':
        p = Pythonsky(sys.argv[2])
        pickle.dump(p, file(sys.argv[3], 'w'))
        exit(0)
    if sys.argv[1] == 'compose':
        p = pickle.load(file(sys.argv[2]))
        print p.make_text_of_expected_length(int(sys.argv[3]))
        exit(0)

    usage()
    exit(0)
