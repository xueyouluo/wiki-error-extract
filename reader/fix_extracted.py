# -*- coding: utf-8 -*-

"""Fixes output of WikiExtractor.py

"""

import argparse
import codecs
import re

import xml.sax
from xml.sax.handler import ContentHandler
handler = ContentHandler()

def fix_revison(revision):
  # fix text
  text_area = False
  new_revison = []
  for x in revision:
    if '<text>' in x:
      text_area = True

    # No </text>
    if text_area and '<sha1>' in x and '</text>' not in x:
      text_area = False
      new_revison.append('</text>')
    
    if text_area:
      # 将text里面的<符号替换掉
      x = x.replace('<text>','##LOSPR##').replace('</text>','##ROSPR##').replace('<','#')
      x = x.replace('##LOSPR##','<text>').replace('##ROSPR##','</text>')
    
    if '</text>' in x:
      text_area = False

    new_revison.append(x)

  try:
    xml.sax.parseString('\n'.join(new_revison),handler)
  except:
    return None
  return new_revison

def fix_extraction(input_dir, input_file, output_dir):
  with codecs.open(input_dir + '/' + input_file, 'r', encoding='utf-8') as f:
      contents = f.read()
      contents = contents.replace("&amp;","&").replace('&lt;','<').replace('&gt;','>').replace('&quot;','"').replace('&apos;','\'')
      contents = re.sub(r'<\/text>\s*<sha1>', '##LOSPR##', contents)
      contents = re.sub(r'<sha1>', '</text>\n\t<sha1>', contents)
      contents = re.sub(r'##LOSPR##', '</text>\n\t<sha1>', contents)
      
      # HTML entities
      contents = re.sub(r'&', '&amp;', contents)

      # Remove HTML tags if not removed already
      tag_pat1 = (r'<\/?(textarea|select|strong|center|option|'
                  r'input|param|small|style|table|tbody|thead|tfoot|'
                  r'body|head|html|span|font|form|'
                  r'div|img|var|pre|sub|sup|var|ref|wiki|'
                  r'br|dl|dt|dd|em|h[1-6]|hr|li|ol|td|tr|th|ul|a|b|p|q|u)>'
                  )
      contents = re.sub(tag_pat1, '', contents)

      # remove bad revisions
      new_content = []
      revison_content = []
      revison_area = False

      for line in contents.splitlines():
        if'<revision>' in line:
          # 如果revision有内容，那么肯定哪里出错了，直接丢弃数据
          if revison_content:
            revison_content = []
          revison_area = True

        if '</revision>' in line:
          revison_content.append(line)
          fixed = fix_revison(revison_content)
          if fixed is not None:
            new_content.extend(fixed)
          revison_content = []
          revison_area = False
          continue

        if revison_area:
          revison_content.append(line)
        else:
          new_content.append(line)
  with codecs.open(output_dir + '/' + input_file, 'w', encoding='utf-8') as fw:
      fw.write('\n'.join(new_content))
      

if __name__ == '__main__':
  arg_parser = argparse.ArgumentParser(description='Script for fixing WikiExtractor.py outputs')
  arg_parser.add_argument('input_dir', help='Input dir')
  arg_parser.add_argument('input_file', help='Input file')
  arg_parser.add_argument('output_dir', help='Output directory')
  args = arg_parser.parse_args()
  fix_extraction(args.input_dir, args.input_file, args.output_dir)
