# -*- coding: utf-8 -*-

"""Extracts spelling errors from revision history. 

"""

import codecs
import re
import utils

class RevisionSentence(object):
  """Class for representing an error sentence together with original sentence.

  """
  def __init__(self, orig_tokens):
    self.orig_tokens = orig_tokens
    self.err_sen = []

  def add_err_sentence(self, err_tokens):
    self.err_sen.append(err_tokens)

  def contains_spelling_errors(self):
    """Whether the earlier revisions of the same sentences have spelling errors.
    
    Returns:
      bool: True or False

    """
    if len(self.err_sen) > 0:
      return True
    else:
      return False

class ErrorCorpus(object):
  """Class for representing the original text data with spelling errors.

  """
  lang = 'english'
  max_dist = 3
  min_sen_len = 3

  def __init__(self, lang='english', max_edit_distance=3, min_sen_len=3):
    self.corpus = None
    self.num_rev = 0
    self.lang = lang
    self.max_edit = max_edit_distance
    self.min_sen_len = min_sen_len

  def create_corpus_from_wiki(self, corpus_root, filename, output_dir):
    create_error_corpus = False
    valid_word_pat = r'(?u)^\w+$'
    sentences = utils.get_sentences_for_text(corpus_root, filename)
    if sentences == None:
      return
    top_rev = []
    top_rev_with_err = []
    try:
      for s_list in sentences:
        s = ''.join(s_list)
        if s.startswith('[Revision timestamp:'):
          self.num_rev += 1
        else:
          if self.num_rev == 1:
            if len(s_list) >= self.min_sen_len:
              rev_sen = RevisionSentence(s_list)
              top_rev.append(rev_sen)
          elif self.num_rev > 1:
            for r in top_rev:
              if len(s_list) == len(r.orig_tokens):
                valid_errors = True
                errors = False
                old_curr_rev_sen = zip(r.orig_tokens, s_list)
                for t in old_curr_rev_sen:
                  dist = utils.levenshtein_distance(t[0], t[1])
                  if dist > 0 and dist <= self.max_dist:
                    # token must be a word 
                    orig_uni = utils.to_unicode_or_bust(t[0])
                    match = re.search(valid_word_pat, orig_uni)
                    if match:
                      errors = True
                  elif dist > self.max_dist:
                    valid_errors = False
                    break
                if errors == True and valid_errors == True:
                  print('errr')
                  r.add_err_sentence(s_list)
                  create_error_corpus = True
                  break
    except AssertionError:
      print('Empty file')

    if create_error_corpus == True:
      with codecs.open(output_dir + '/' + filename, 'w', 'utf-8', errors='ignore') as f:
        for r in top_rev:
          if r.contains_spelling_errors() == True:
            orig_sen = ' '.join(r.orig_tokens)
            err_as_sen = map(lambda x: ' '.join(x), r.err_sen)
            orig_err_sen = [orig_sen] + list(err_as_sen)
            to_write_uni = '####'.join(orig_err_sen)
            f.write(to_write_uni + u'\n')

if __name__ == '__main__':
  import argparse
  arg_parser = argparse.ArgumentParser(description='Script for extracting spelling errors from a revision history')
  arg_parser.add_argument('corpus_root', help='The directory in which the revision file exists')
  arg_parser.add_argument('input_file', help='Revision file')
  arg_parser.add_argument('output_dir', help='Output directory')
  arg_parser.add_argument('lang', help='Language of the text data')
  arg_parser.add_argument('max_edit', help='Maximum edit distance between the correct word and the misspelled work')

  args = arg_parser.parse_args()
  err_corpus = ErrorCorpus(args.lang.lower(), args.max_edit)
  err_corpus.create_corpus_from_wiki(args.corpus_root, args.input_file, args.output_dir)

  #import os
  #corpus_root = '/net/cluster/TMP/loganathan/wiki_dump/cs/processing/stage3'
  #for root, dirnames, filenames in os.walk(corpus_root):
  #  for f in filenames:
  #    err_corpus = ErrorCorpus()
  #    print 'Extracting errors from: ', f
  #    err_corpus.create_corpus_from_wiki(corpus_root, f, '')

  #corpus_root = '/net/cluster/TMP/loganathan/wiki_dump/cs/processing/tmp_out'
  #file_name = 'hello.txt'
  #err_corpus = ErrorCorpus()
  #err_corpus.create_corpus_from_wiki(corpus_root, file_name, '')
