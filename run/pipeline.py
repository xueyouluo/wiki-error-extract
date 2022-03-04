import subprocess
import time
import os
import logging
import copy
from glob import glob

import threading
from multiprocessing import Process
import multiprocessing as mp

def run_bash(args,cmd):
    cmd = cmd.format(**args)
    print('cmd:',cmd)
    os.system(cmd)

def check_output_dir(output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

POOL_SIZE = 9
MAX_EDIT = 0.1
MIN_FILESIZE = 5 # KB

global_args = {
    "code_root" : '/nfs/users/xueyou/github/wiki-error-corpus',
    # "xml_dump": '/nfs/users/xueyou/data/speller/wiki/zhwiki-20211201-pages-meta-history1.xml-p2981p11534',
    "input_dir" : '/data/xueyou/data/speller/wiki/',
    "output_dir" : '/data/xueyou/data/speller/wiki/',
    'max_edit': MAX_EDIT
    }

for xml_dump_file in list(glob('/data/xueyou/data/speller/wiki/*.7z')):
  global_args['xml_dump'] = xml_dump_file.replace('.7z','')

  # Stage 1
  # Extract 7z file
  print(f'extract {xml_dump_file}')
  cmd = f'7z e {xml_dump_file}'
  run_bash({},cmd)

  # Stage 2
  # Divide the large XML revision dump file into per page revisions.
  print(f'divide XML file')
  cmd = 'python {code_root}/reader/divide_xml_revisions.py {xml_dump} {output_dir}'
  args = copy.deepcopy(global_args)
  args['output_dir'] = args['output_dir'] + 'stage1'
  check_output_dir(args['output_dir'])
  run_bash(args,cmd)


  # Stage 3
  # Extract Revisions from page history
  cmd = 'python {code_root}/reader/extract_revisions_new.py {input_dir} {input_file} {output_dir}'
  input_dir = global_args['input_dir'] + 'stage1'
  output_dir = global_args['output_dir'] + 'stage3'
  check_output_dir(output_dir)

  pool = mp.Pool(processes = POOL_SIZE)
  for fname in glob(input_dir + '/*.xml'):
    fsize = os.path.getsize(fname) / 1024 # KB
    if fsize < MIN_FILESIZE:
      # print(f'small size, skip {fname}')
      continue
    args = copy.deepcopy(global_args)
    args['input_dir'] = input_dir
    args['output_dir'] = output_dir
    args['input_file'] = os.path.basename(fname)
    pool.apply_async(run_bash,(args, cmd))
  pool.close()
  pool.join()

  # Stage 4
  # Extract errors with edit distance
  cmd = 'python {code_root}/reader/extract_spelling_errors_new.py {input_dir} {input_file} {output_dir} zh {max_edit}'
  input_dir = global_args['input_dir'] + 'stage3'
  output_dir = global_args['output_dir'] + 'stage4'
  check_output_dir(output_dir)

  pool = mp.Pool(processes = POOL_SIZE)
  for fname in glob(input_dir + '/*.xml'):
    basename = os.path.basename(fname)
    args = copy.deepcopy(global_args)
    args['input_dir'] = input_dir
    args['output_dir'] = output_dir
    args['input_file'] = basename
    pool.apply_async(run_bash,(args, cmd))
  pool.close()
  pool.join()

  # Stage5
  # collect all the errors
  input_dir = global_args['input_dir'] + 'stage4'
  output_dir = global_args['input_dir'] + 'stage5'
  check_output_dir(output_dir)
  with open(output_dir + '/error_sent.txt','a') as ef,open(output_dir + '/ori_sent.txt','a') as of:
    for fname in glob(input_dir + '/*.xml_error_sen.txt'):
      basename = os.path.basename(fname).split('.')[0]
      # err_f.write(open(input_dir + '/' + basename + '.xml_spelling_error.txt').read())
      ef.write(open(input_dir + '/' + basename + '.xml_error_sen.txt').read())
      of.write(open(input_dir + '/' + basename + '.xml_orig_sen.txt').read())

  # Stage 6
  # clear 
  print('clear tmp files')
  cmd = f'''rm {global_args['xml_dump']}
  rm -rf stage1 stage3 stage4
  mv {xml_dump_file} extracted
  '''
  run_bash({},cmd)
print('all done')




