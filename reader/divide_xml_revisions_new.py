# -*- coding: utf-8 -*-

"""Divide the large XML revision dump file into per page revisions.

"""
import codecs
import os
import xml.sax
import xml.sax.saxutils
import io
import json
from extract_revisions_new import extract_revisions
from extract_spelling_errors_new import converter,check_error

html_escape_table = {
  u'‘': "&apos;",
  u'’': "&apos;",
  u'“': '&quot;',
  u'”': '&quot;'
}

html_unescape_table = {v:k for k, v in html_escape_table.items()}

def html_escape(text):
  return xml.sax.saxutils.escape(text, html_escape_table)

def html_unescape(text):
  return xml.sax.saxutils.unescape(text, html_unescape_table)


def extract_errors(content,number_of_edits,outfile):
  buffer = ''
  # extract revisions
  for timestamp,text in extract_revisions(io.StringIO(content)):
    if len(text) > 10:
      buffer += '\n\n[Revision timestamp: ' + timestamp + ']\n\n'
      buffer += text

  revisions = []
  line = []

  srcs,tgts = [],[]
  pre_revision = ''
  current_revision = ''
  cnt = 0
  for line in buffer.splitlines():
    line = converter.convert(line)
    if "Revision timestamp" in line:
      if current_revision:
        if pre_revision:
          cnt += 1
          # if cnt % 100 == 0:
          #   print('processed',cnt)
          check_error(pre_revision,current_revision.strip(),srcs,tgts,number_of_edits)
      pre_revision = current_revision.strip()
      current_revision = ''
    else:
      current_revision += line
  if current_revision and pre_revision:
    check_error(pre_revision,current_revision.strip(),srcs,tgts,number_of_edits)

  
  keeps = []
  if srcs:
    errors = set()
    for src,tgt in zip(srcs[::-1],tgts[::-1]):
      if src in errors or tgt in errors:
        continue
      errors.add(src)
      errors.add(tgt)
      keeps.append({"src":src,'tgt':tgt})

  if keeps:
    for x in keeps:
      outfile.write(json.dumps(x,ensure_ascii=False) + '\n')

class WikiRevisionDumpHandler(xml.sax.ContentHandler):
  wiki_dump_tags = set(['page', 'title', 'ns', 'id', 'revision', 'parentid',
                        'timestamp', 'contributor', 'ip', 'username', 
                        'comment', 'model', 'format', 'text', 'sha1'])
  file_counter = 0
  file_handle = '' 
 
  def __init__(self, input_file, output_file, number_of_edits):
    # Input/output locations
    self.input_file = input_file
    self.output_file = open(output_file,'a')
    self.number_of_edits = number_of_edits

    # Recent tag visited by SAX parser
    self.curr_tag = ''
    self.content = ''

  def startElement(self, tag, attributes):
    self.curr_tag = tag
    if self.curr_tag == 'page': 
      # close the unclosed handles first if any
      if self.file_handle:
        self.file_handle = ''
      self.file_handle += self.tag_start('page')+'\n'
    elif self.curr_tag in self.wiki_dump_tags:
      self.file_handle += self.tag_start(self.curr_tag)    
      
  def endElement(self, tag):
    self.curr_tag = tag
    if self.curr_tag == 'page': 
      self.file_handle += self.tag_end('page')
      self.file_counter += 1
      extract_errors(self.file_handle,self.number_of_edits,self.output_file)
      self.file_handle = ''
      # if self.file_counter % 100 == 0:
      print(f'{self.input_file} processed {self.file_counter} pages')
    elif self.curr_tag in self.wiki_dump_tags:
      self.file_handle += self.tag_end(self.curr_tag)     

  def characters(self, contents):
    self.content = contents  
    if self.curr_tag != 'page' and self.curr_tag in self.wiki_dump_tags:
      self.file_handle += html_escape(self.content)
 
  @staticmethod    
  def surround_wih_tag(tag, cont): return '<'+tag+'>'+cont+'</'+tag+'>'

  @staticmethod
  def tag_start(tag): return '<'+tag+'>'
  
  @staticmethod
  def tag_end(tag): return '</'+tag+'>'
    

if __name__ == '__main__':
  import argparse
  arg_parser = argparse.ArgumentParser(description='Script for dividing the large XML revision dump into individual page revisions.')
  arg_parser.add_argument('input_file', help='XML revision dump file name')
  arg_parser.add_argument('output_file', help='Output file')
  arg_parser.add_argument('number_of_edits', help='number_of_edits')
  args = arg_parser.parse_args()
  number_of_edits = float(args.number_of_edits)
  if not os.path.exists(os.path.dirname(args.output_file)):
    os.makedirs(os.path.dirname(args.output_file))

  # SAX XML reader
  xml_parser = xml.sax.make_parser()
  
  revision_dump_handler = WikiRevisionDumpHandler(args.input_file, args.output_file,number_of_edits)
  xml_parser.setContentHandler(revision_dump_handler)
  xml_parser.parse(args.input_file)
