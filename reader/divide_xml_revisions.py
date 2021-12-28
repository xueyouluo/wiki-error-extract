# -*- coding: utf-8 -*-

"""Divide the large XML revision dump file into per page revisions.

"""
import codecs
import os
import xml.sax
import xml.sax.saxutils


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


class WikiRevisionDumpHandler(xml.sax.ContentHandler):
  wiki_dump_tags = set(['page', 'title', 'ns', 'id', 'revision', 'parentid',
                        'timestamp', 'contributor', 'ip', 'username', 
                        'comment', 'model', 'format', 'text', 'sha1'])
  file_counter = 0
  file_handle = '' 
 
  def __init__(self, input_file, output_dir):
    # Input/output locations
    self.input_file = input_file
    self.output_dir = output_dir

    # Recent tag visited by SAX parser
    self.curr_tag = ''
    self.content = ''

  def startElement(self, tag, attributes):
    self.curr_tag = tag
    if self.curr_tag == 'page': 
      # close the unclosed handles first if any
      if self.file_handle:
        self.file_handle.close()
      fname = repr(self.file_counter).zfill(10) + '.xml'
      abspath = self.output_dir + '/' + fname
      print('Writing to file: ', abspath )
      self.file_handle = codecs.open(abspath, 'w', 'utf-8')
      self.file_handle.write(self.tag_start('page')+'\n')
    elif self.curr_tag in self.wiki_dump_tags:
      self.file_handle.write(self.tag_start(self.curr_tag))      
      
  def endElement(self, tag):
    self.curr_tag = tag
    if self.curr_tag == 'page': 
      self.file_handle.write(self.tag_end('page'))
      self.file_handle.close()
      self.file_counter += 1
    elif self.curr_tag in self.wiki_dump_tags:
      self.file_handle.write(self.tag_end(self.curr_tag))      

  def characters(self, contents):
    self.content = contents  
    if self.curr_tag != 'page' and self.curr_tag in self.wiki_dump_tags:
      self.file_handle.write(html_escape(self.content))
 
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
  arg_parser.add_argument('output_dir', help='Output directory')
  args = arg_parser.parse_args()
  if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

  # SAX XML reader
  xml_parser = xml.sax.make_parser()
  
  revision_dump_handler = WikiRevisionDumpHandler(args.input_file, args.output_dir)
  xml_parser.setContentHandler(revision_dump_handler)
  xml_parser.parse(args.input_file)
