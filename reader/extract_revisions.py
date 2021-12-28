# -*- coding:utf-8 -*-

import codecs
import os
import xml.sax
import xml.sax.saxutils

from fix_extracted import fix_extraction


html_escape_table = {
  u'‘': "&apos;",
  u'’': "&apos;",
  u'“': '&quot;',
  u'”': '&quot;',
  u'&': '&amp;'
}

html_unescape_table = {v:k for k, v in html_escape_table.items()}

def html_escape(text):
  return xml.sax.saxutils.escape(text, html_escape_table)

def html_unescape(text):
  return xml.sax.saxutils.unescape(text, html_unescape_table)


class WikiRevisionHandler(xml.sax.ContentHandler):
  input_file = 'wiki.xml'
  output_dir = '.'
  wiki_dump_tags = set(['page', 'title', 'ns', 'id', 'revision', 'parentid',
                        'timestamp', 'contributor', 'ip', 'username', 
                        'comment', 'model', 'format', 'text', 'sha1'])
  file_handle = ''  

  def __init__(self, input_file, output_file):
    # Input/output locations
    self.input_file = input_file
    self.output_file = output_file

    # Recent tag visited by SAX parser
    self.curr_tag = ''
    self.content = ''
    
    # Revisions
    self.revisions = []
    self.curr_rev = []
    self.rev_start = False
    self.ts_start = False
    self.timestamps = []
    
    
  def startElement(self, tag, attributes):
    self.curr_tag = tag
    if self.curr_tag == 'timestamp':
      self.ts_start = True
    if self.curr_tag == 'revision':
      self.rev_start = True
    if self.curr_tag == 'page': 
      # close the unclosed handles first if any
      if self.file_handle:
        self.file_handle.close()
      print('Writing to file: ', self.output_file)
      self.file_handle = codecs.open(self.output_file, 'w', 'utf-8')
    #  self.file_handle.write(self.tag_start('page')+'\n')
    #elif self.curr_tag in self.wiki_dump_tags:
    #  self.file_handle.write(self.tag_start(self.curr_tag))      
      
  def endElement(self, tag):
    self.curr_tag = tag
    if self.curr_tag == 'timestamp':
      self.ts_start = False
    if self.curr_tag == 'revision':
      self.rev_start = False
      if len(self.curr_rev) > 0:
        self.revisions.append(self.curr_rev)
        self.curr_rev = []
    if self.curr_tag == 'page': 
    #  self.file_handle.write(self.tag_end('page'))
      print('revisions',len(self.revisions))
      ts_revs = list(zip(self.timestamps, self.revisions))
      for t_r in ts_revs[::-1]:
        self.file_handle.write('\n[Revision timestamp: ' + t_r[0] + ']\n')
        html_escaped = html_escape(''.join(t_r[1]))
        self.file_handle.write(html_escaped)        
      self.file_handle.close()
    #elif self.curr_tag in self.wiki_dump_tags:
    #  self.file_handle.write(self.tag_end(self.curr_tag))      

  def characters(self, contents):
    self.content = contents  
    if self.curr_tag == 'text' and self.rev_start:
      self.curr_rev.append(self.content)
    if self.curr_tag == 'timestamp' and self.ts_start:
      self.timestamps.append(self.content)
      #self.file_handle.write('[Revision timestamp: ' + self.content + ']\n')
    #if self.curr_tag != 'page' and self.curr_tag in self.wiki_dump_tags:
    #  self.file_handle.write(html_escape(self.content))

 
class WikiRevErrorHandler(xml.sax.handler.ErrorHandler):

  def error(self, exception):
    pass

  def fatalError(self, exception):
    pass  
  
  def warning(self, exception):
    pass



if __name__ == '__main__':
  import argparse
  arg_parser = argparse.ArgumentParser(description='Script for dividing the large XML revision dump into individual page revisions.')
  arg_parser.add_argument('input_dir', help='Input dir')
  arg_parser.add_argument('input_file', help='Input file')
  arg_parser.add_argument('output_dir', help='Output dir')
  args = arg_parser.parse_args()

  # fix extraction
  fix_extraction(args.input_dir,args.input_file,args.input_dir)

  input_file = args.input_dir + '/' + args.input_file
  output_file = args.output_dir + '/' + args.input_file
  # SAX XML reader
  xml_parser = xml.sax.make_parser()
  
  revision_handler = WikiRevisionHandler(input_file, output_file)
  wiki_err_handler = WikiRevErrorHandler()
  xml_parser.setContentHandler(revision_handler)
  xml_parser.setErrorHandler(wiki_err_handler)
  xml_parser.parse(input_file)

