import re
import logging
from wikiextractor.extract import Extractor

extractor = Extractor('##NoName##')


def clean_revison(revision):
    # fix text
    revision = '\n'.join(revision)

    m = re.search(r'<text>(.*?)</text>', revision, flags=re.DOTALL)
    if m:
        text = m.group(1)
    else:
        logging.warning('Missing text element')
        return None
    
    text = extractor.extract(text)
    m = re.search(r'<timestamp>(.*?)</timestamp>', revision)
    timestamp = 'none'
    if m:
        timestamp = m.group(1)
    return (timestamp,text)

def extract_revisions(fname):
    revision_cnt = 0
    revison_content = []
    revison_area = False
    if isinstance(fname,str):
      fname = open(fname)
    for line in fname:
        if'<revision>' in line:
          # 如果revision有内容，那么肯定哪里出错了，直接丢弃数据
          if revison_content:
            revison_content = []
          revison_area = True

        if '</revision>' in line:
          revision_cnt += 1
          if revision_cnt % 100 == 0:
              print(fname, 'revision cnt', revision_cnt)
          revison_content.append(line)
          fixed = clean_revison(revison_content)
          if fixed is not None:
            yield fixed
          revison_content = []
          revison_area = False
          continue

        if revison_area:
          revison_content.append(line)



if __name__ == '__main__':
  import argparse
  arg_parser = argparse.ArgumentParser(description='Script for dividing the large XML revision dump into individual page revisions.')
  arg_parser.add_argument('input_dir', help='Input dir')
  arg_parser.add_argument('input_file', help='Input file')
  arg_parser.add_argument('output_dir', help='Output dir')
  args = arg_parser.parse_args()


  input_file = args.input_dir + '/' + args.input_file
  output_file = args.output_dir + '/' + args.input_file
  with open(output_file,'w') as f:
      for timestamp,text in extract_revisions(input_file):
          if len(text) > 10:
            f.write('\n\n[Revision timestamp: ' + timestamp + ']\n\n')
            f.write(text)


