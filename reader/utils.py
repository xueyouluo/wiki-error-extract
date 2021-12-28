# *-* coding: utf-8 *-*

"""Utility functions.

"""
# import nltk.data
# from nltk.tokenize.regexp import WhitespaceTokenizer
# from nltk.corpus import PlaintextCorpusReader
import jieba
import numpy as np
import sys

import re
from typing import List

def is_chinese_char(cp):
  """Checks whether CP is the codepoint of a CJK character."""
  # This defines a "chinese character" as anything in the CJK Unicode block:
  #   https://en.wikipedia.org/wiki/CJK_Unified_Ideographs_(Unicode_block)
  #
  # Note that the CJK Unicode block is NOT all Japanese and Korean characters,
  # despite its name. The modern Korean Hangul alphabet is a different block,
  # as is Japanese Hiragana and Katakana. Those alphabets are used to write
  # space-separated words, so they are not treated specially and handled
  # like the all of the other languages.
  cp = ord(cp)
  if ((cp >= 0x4E00 and cp <= 0x9FFF) or  #
      (cp >= 0x3400 and cp <= 0x4DBF) or  #
      (cp >= 0x20000 and cp <= 0x2A6DF) or  #
      (cp >= 0x2A700 and cp <= 0x2B73F) or  #
      (cp >= 0x2B740 and cp <= 0x2B81F) or  #
      (cp >= 0x2B820 and cp <= 0x2CEAF) or
      (cp >= 0xF900 and cp <= 0xFAFF) or  #
      (cp >= 0x2F800 and cp <= 0x2FA1F)):  #
    return True

  return False

def split_sentence(document: str, flag: str = "all", limit: int = 510) -> List[str]:
    """
    Args:
        document:
        flag: Type:str, "all" 中英文标点分句，"zh" 中文标点分句，"en" 英文标点分句
        limit: 默认单句最大长度为510个字符
    Returns: Type:list
    """
    sent_list = []
    try:
        if flag == "zh":
            document = re.sub('(?P<quotation_mark>([。？！…](?![”’"\'])))', r'\g<quotation_mark>\n', document)  # 单字符断句符
            document = re.sub('(?P<quotation_mark>([。？！]|…{1,2})[”’"\'])', r'\g<quotation_mark>\n', document)  # 特殊引号
        elif flag == "en":
            document = re.sub('(?P<quotation_mark>([.?!](?![”’"\'])))', r'\g<quotation_mark>\n', document)  # 英文单字符断句符
            document = re.sub('(?P<quotation_mark>([?!.]["\']))', r'\g<quotation_mark>\n', document)  # 特殊引号
        else:
            document = re.sub('(?P<quotation_mark>([。？！….?!](?![”’"\'])))', r'\g<quotation_mark>\n', document)  # 单字符断句符
            document = re.sub('(?P<quotation_mark>(([。？！.!?]|…{1,2})[”’"\']))', r'\g<quotation_mark>\n',
                              document)  # 特殊引号

        sent_list_ori = document.splitlines()
        for sent in sent_list_ori:
            sent = sent.strip()
            if not sent:
                continue
            else:
                while len(sent) > limit:
                    temp = sent[0:limit]
                    sent_list.append(temp)
                    sent = sent[limit:]
                sent_list.append(sent)
    except:
        sent_list.clear()
        sent_list.append(document)
    return sent_list


def to_unicode_or_bust(s, encoding='utf-8'):
  """Converts the bytestring in utf-8 to Unicode.

  Credit: Method from 'Unicode in Python, Completely Demystified'.
  
  Args:
    s: Bytestring
    encoding: Encoding

  Returns:
    Return the Unicode version of the given bytestring

  """
  # if isinstance(s, str):
  #   if not isinstance(s, unicode):
  #     s = unicode(s, encoding)
  return s   


def get_sentences_for_text(corpus_root, filename, lang='english'):
  """Segments the given text into sentences.

  Args:
    corpus_root: Directory in which the text file is residing.
    filename: Name of the text file.
    lang: Tokenizer language. For possible values, look at:
    ${NLTK_DATA}/tokenizers/punkt

  Returns:
    Sentences in the given text. 

  """
  sents = []
  for s in split_sentence(open(corpus_root + '/' + filename).read()):
    sents.append(jieba.lcut(s))
  return sents
  # tokenizer_path = 'tokenizers/punkt/' + lang + '.pickle'
  # text = PlaintextCorpusReader(corpus_root, [filename], word_tokenizer=WhitespaceTokenizer(), 
  #                              sent_tokenizer=nltk.data.LazyLoader(tokenizer_path))
  # return text.sents()

def levenshtein_distance(s, t):
  """Minimum edit distance between two strings.

  Args:
    s: Source string
    t: Target string

  Returns:
    int: Minimum edit distance between the two input strings.

  """
  m = len(s)
  n = len(t)
  if m == 0:
    return n
  if n == 0:
    return m
  d = np.zeros((m+1, n+1))
  d[:, 0] = np.arange(m+1)
  d[0, :] = np.arange(n+1)
  for j in range(1, n+1):
    for i in range(1, m+1):
      if s[i-1] == t[j-1]:
        d[i][j] = d[i-1][j-1]
      else:
        d[i][j] = min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+1)
  return int(d[m][n])


if __name__ == '__main__':
  corpus_root = '/net/cluster/TMP/loganathan/wiki_dump/cs/processing/stage3'
  file_name = '0000000007.xml'
  sentences = get_sentences_for_text(corpus_root, file_name)
  # try:
  #   for s in sentences:
  #     print s
  #     print '\n----END----'
  # except AssertionError:
  #   print 'Empty file'
  
