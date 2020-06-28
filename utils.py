from Levenshtein import StringMatcher


def fingerprints_to_words(text, range_=range(2, 7)):
    """
    Each fingerprint is split into words of 2 to 6 letters.
    This is shingling
    """
    words = []
    for num_letters in range_:
        words.extend(split_in_words(text, num_letters))

    return words


def split_in_words(text, num_letters):
    """
    Split a long text (without space) into words of num_letters letters.
    For instance if text is niijighkqj and num_letters is 4, will return
    ["niij", "iiji", "ijig", "jigh", "ighk", "ghkg", "hkgj"]
    :param text: Text to split into words
    :param num_letters: Size of each word
    :return: A list of words representing the text
    """
    words = []
    for i in range(0, len(text)):
        if i + num_letters > len(text):
            break
        w = text[i:i+num_letters]
        words.append(w)
    return list(set(words))


def distance_levenshtein(text_1, text_2):
    """
    In levenshtein, the lowest score is an exact match. Invert this behavior.
    Higest score must be highest match. Based on longest string.
    :param text_1:
    :param text_2:
    :return:
    """
    sm = StringMatcher
    dist = sm.distance(text_1, text_2)
    score = max(len(text_1), len(text_2)) - dist
    return score


def distance_commonwords(text_1, text_2):
    """
    Will first split fingerprints into words, for example
    hiiaj becomes ["hi", "ii", "ia", "aj", "hii", "iia", "iaj", "hiia", "iiaj", "hiiaj"]
    and then count the words in common.
    :param text_1: Fingerprint 1 to compare
    :param text_2: Fingerprint 2 to compare
    :return:
    """
    list_1 = fingerprints_to_words(text_1)
    list_2 = fingerprints_to_words(text_2)
    dist = 0
    for word in list_1:
        if word in list_2:
            dist += 1

    return dist



def distance_commonwords_ponderation(text_1, text_2):
    """
    Will first split fingerprints into words, for example
    hiiaj becomes ["hi", "ii", "ia", "aj", "hii", "iia", "iaj", "hiia", "iiaj", "hiiaj"]
    and then count the words in common.

    Ponderate it by the similarity of number of words from one fingerprint to the other.

    :param text_1: Fingerprint 1 to compare
    :param text_2: Fingerprint 2 to compare
    :return:
    """
    list_1 = fingerprints_to_words(text_1)
    list_2 = fingerprints_to_words(text_2)
    dist = 0
    for word in list_1:
        if word in list_2:
            dist += 1

    ponderation = min(len(list_1), len(list_2))/max(len(list_1), len(list_2))

    return dist * ponderation