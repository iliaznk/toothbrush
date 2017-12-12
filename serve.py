# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys, os, glob, codecs

import flask
from flask import request

import config

app = flask.Flask(__name__)
port = 4057

if not os.path.exists(config.DIR_PATH_META):
  os.mkdir(config.DIR_PATH_META)

dir_path = os.path.expanduser(config.DIR_PATH_NOTES)
open_counts_path = os.path.join(config.DIR_PATH_META, 'open_counts.json')
selected_index = None

basename_to_content = {}
basename_to_content_lower = {}
glob_path = os.path.join(dir_path, '*.txt')
for path in glob.glob(glob_path):
  basename = os.path.splitext(os.path.basename(path))[0]
  with codecs.open(path, encoding='utf-8') as f:
    basename_to_content[basename] = f.read()
  basename_to_content_lower[basename] = basename_to_content[basename].lower()

basename_to_open_count = {}
if os.path.exists(open_counts_path):
  with open(open_counts_path) as f:
    text = f.read()
  try:
    basename_to_open_count = json.loads(text)
  except Exception:
    pass

@app.route('/search', methods=['POST'])
def search():
  matched_basenames = []
  query_string = unicode(request.json['query'])

  terms = set(query_string.lower().split())
  for basename, content in basename_to_content_lower.iteritems():
    for term in terms:
      try:
        if term not in basename and term not in content:
          break
      except:
        print 'error searching:',
    else:
      matched_basenames.append(basename)

  matched_basenames.sort(key=lambda basename: score(query_string, basename), reverse=True)
  num_matches_to_show = 10

  out_lines = []
  for i, basename in enumerate(matched_basenames[:num_matches_to_show]):
    out_lines.append('{}{}'.format('> ' if i == selected_index else '  ', basename))
    if i == selected_index:
      full_text = basename_to_content[basename].strip()
      lines = full_text.splitlines()
      out_lines += ['     ' + line for line in lines]

  if not matched_basenames:
    out_lines.append('~ nothing found ~')
  elif len(matched_basenames) > num_matches_to_show:
    out_lines.append('  ...')

  return '\n'.join(out_lines)

@app.route('/reload', methods=['POST'])

def score(query_string, basename):
  score = 0
  if query_string == basename:
    score += 10
  score += basename_to_open_count.get(basename, 0)
  return score

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=port, debug=(port != 80), threaded=True)
