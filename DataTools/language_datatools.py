# coding: utf-8
"""
This module is based off of the below article:
http://fjavieralba.com/basic-sentiment-analysis-with-python.html

I took what Javiar was doing and ran with it. A 1000 thanks mate :-)
"""

import nltk
import yaml


def split(text):
    """
    input format: a paragraph of text
    output format: a list of lists of words.
        e.g.: [['this', 'is', 'a', 'sentence'], ['this', 'is', 'another', 'one']]
    """

    nltk_splitter = nltk.data.load('tokenizers/punkt/english.pickle')
    nltk_tokenizer = nltk.tokenize.TreebankWordTokenizer()
    return [nltk_tokenizer.tokenize(sent) for sent in nltk_splitter.tokenize(text)]


def pos_tag(sentences):
    """
    input format: list of lists of words
        e.g.: [['this', 'is', 'a', 'sentence'], ['this', 'is', 'another', 'one']]
    output format: list of lists of tagged tokens. Each tagged tokens has a
    form, a lemma, and a list of tags
        e.g: [[('this', 'this', ['DT']), ('is', 'be', ['VB']), ('a', 'a', ['DT']), ('sentence', 'sentence', ['NN'])],
                [('this', 'this', ['DT']), ('is', 'be', ['VB']), ('another', 'another', ['DT']),
                ('one', 'one', ['CARD'])]]
    """

    pos = [nltk.pos_tag(sentence) for sentence in sentences]
    # adapt format
    pos = [[(word, word, [postag]) for (word, postag) in sentence] for sentence in pos]
    return pos


class DictionaryTagger(object):
    """
        Class to tag sentences
    """
    def __init__(self, dictionary_paths):
        """
            Opens YAML files and instantiates object of type DictionaryTagger
        :param dictionary_paths:
        """
        files = [open(path, 'r') for path in dictionary_paths]
        dictionaries = [yaml.load(dict_file) for dict_file in files]
        map(lambda x: x.close(), files)
        self.dictionary = {}
        self.max_key_size = 0
        for curr_dict in dictionaries:
            for key in curr_dict:
                if key in self.dictionary:
                    self.dictionary[key].extend(curr_dict[key])
                else:
                    self.dictionary[key] = curr_dict[key]
                    self.max_key_size = max(self.max_key_size, len(key))

    def tag(self, postagged_sentences):
        """
            Tags sentences with internal tags for positive and negative
        :param postagged_sentences:
        :return: tagged sentences
        """
        return [self.tag_sentence(sentence) for sentence in postagged_sentences]

    def tag_sentence(self, sentence, tag_with_lemmas=False):
        """
        the result is only one tagging of all the possible ones.
        The resulting tagging is determined by these two priority rules:
            - longest matches have higher priority
            - search is made from left to right
        """

        tag_sentence = []
        N = len(sentence)

        if self.max_key_size == 0:
            self.max_key_size = N
        i = 0

        while i < N:
            j = min(i + self.max_key_size, N)  # avoid overflow
            tagged = False

            while j > i:
                expression_form = ' '.join([word[0] for word in sentence[i:j]]).lower()
                expression_lemma = ' '.join([word[1] for word in sentence[i:j]]).lower()

                if tag_with_lemmas:
                    literal = expression_lemma
                else:
                    literal = expression_form
                if literal in self.dictionary:
                    # self.logger.debug("found: %s" % literal)
                    is_single_token = j - i == 1
                    original_position = i
                    i = j
                    taggings = [tag for tag in self.dictionary[literal]]
                    tagged_expression = (expression_form, expression_lemma, taggings)
                    if is_single_token:  # if the tagged literal is a single token, conserve its previous taggings:
                        original_token_tagging = sentence[original_position][2]
                        tagged_expression[2].extend(original_token_tagging)
                    tag_sentence.append(tagged_expression)
                    tagged = True
                else:
                    j = j - 1
            if not tagged:
                tag_sentence.append(sentence[i])
                i += 1
        return tag_sentence


def __value_of(sentiment):
    """
        Internal method to quantify polarity
    :param sentiment:
    :return:
    """
    if sentiment == 'positive': return 1
    if sentiment == 'negative': return -1
    return 0


def network_score(network, add_polarity=True, flag_changes=True):
    """
    Runs Sentiment analysis on a network and returns an analyzed and scored network.
    :param network:
    :param add_polarity:
    :param flag_changes:
    :return: scored network
    """
    score = []
    for chunk in network['Data']:
        split_sentences = split(chunk)
        pos_sentences = pos_tag(split_sentences)
        tagged_sentences = DictionaryTagger(['positive.yml', 'negative.yml', 'inv.yml']).tag(pos_sentences)
        relationship_score = sentiment_score(tagged_sentences)

        score.append(relationship_score)

    network['Sentiment Score'] = score

    if add_polarity:
        polarity = []
        for sc in score:
            if sc > 0:
                polarity.append('positive')
            elif sc < 0:
                polarity.append('negative')
            else:
                polarity.append('unknown')

        network['Polarity'] = polarity

    if flag_changes:
        network.loc[network['Polarity'] != network['PS_Polarity'], 'Polarity_Changed'] = True
        network.loc[network['Polarity'] == network['PS_Polarity'], 'Polarity_Changed'] = False

    return network


def sentence_score(sentence_tokens, previous_token, acum_score):
    """
        scores sentences thats been tagged.
    :param sentence_tokens:
    :param previous_token:
    :param acum_score:
    :return:
    """
    if not sentence_tokens:
        return acum_score
    else:
        current_token = sentence_tokens[0]
        tags = current_token[2]
        token_score = sum([__value_of(tag) for tag in tags])
        if previous_token is not None:
            previous_tags = previous_token[2]
            # if 'inc' in previous_tags:
            #    token_score *= 2.0
            # elif 'dec' in previous_tags:
            #    token_score /= 2.0
            if 'inv' in previous_tags:
                token_score *= -1.0
        return sentence_score(sentence_tokens[1:], current_token, acum_score + token_score)


def sentiment_score(review):
    """
    Returns cumulative score of scored sentences
    :param review:
    :return:
    """
    return sum([sentence_score(sentence, None, 0.0) for sentence in review])


def weighted_sentence_score(sentence_tokens):
    """
    Weighted score...
    :param sentence_tokens:
    :return: Totally arbitrary weight based on hokey pokey
    """
    tags = []
    for x in range(len(sentence_tokens)):
        tags.append(sentence_tokens[x][2])
    return sum([__value_of(tag[0]) / len(sentence_tokens) for tag in tags])


def weighted_sentiment_score(review, matrix_flag):
    """
        Totally arbitrary weight based on hokey pokey
    :param review:
    :param matrix_flag:
    :return: Totally arbitrary weight based on hokey pokey
    """
    if matrix_flag:
        return [weighted_sentence_score(sentence) for sentence in review]
    else:
        return sum([weighted_sentence_score(sentence) for sentence in review])
