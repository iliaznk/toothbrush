#!/usr/bin/python
import sys, tty, termios, subprocess, os, json, glob

import requests

import config

def getch():
  # Return a single character from stdin.

  fd = sys.stdin.fileno()
  old_settings = termios.tcgetattr(fd)
  try:
    tty.setraw(sys.stdin.fileno())
    ch = sys.stdin.read(1)
  finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
  return ch

def open_selected():
  if selected_index is None:
    for i in range(len(matched_basenames)):
      open_index(i)
    return
  open_index(selected_index)

def open_index(index):
  basename = matched_basenames[:10][index]
  path = os.path.join(dir_path, basename) + '.txt'
  open_path(path)

def open_path(path):
  print 'opening:'
  print '"{}"'.format(path)

  basename = os.path.basename(path)
  basename_to_open_count.setdefault(basename, 0)
  basename_to_open_count[basename] += 1
  with open(open_counts_path, 'w') as f:
    f.write(json.dumps(basename_to_open_count))

  os.system('open "{}"'.format(path))

def new_note(query_string):
  new_path = os.path.join(DIR_PATH_NOTES, query_string) + '.txt'
  with open(new_path, 'w') as f:
    f.write('')
  open_path(new_path)

def adjust_selection(amount):
  if not matched_basenames:
    selected_index = None
    return

  if selected_index is None:
    selected_index = 0
  else:
    selected_index += amount
  selected_index %= min(len(matched_basenames), 10)

def main_loop():
  # Wait for a key, build up the query string.

  query_string = ' '.join(sys.argv[1:])
  query_path = os.path.join(config.DIR_PATH_META, 'saved_query.txt')
  if not query_string.strip() and os.path.exists(query_path):
    with open(query_path) as f:
      query_string = f.read()

  first_char_typed = False
  while True:
    print '\nquery: {}\n'.format(query_string)

    headers = {'content-type': 'application/json'}
    resp = requests.post(
      'http://127.0.0.1:4057/search',
      json.dumps({'query': 'foo'}),
      headers=headers
    )
    print resp.content

    ch = getch()

    if ord(ch) == 3:  # ctrl+c
      raise KeyboardInterrupt
    elif ord(ch) == 23:  # ctrl+w
      query_string = query_string.rsplit(' ', 1)[0] if ' ' in query_string else ''
    elif ord(ch) == 127:  # backspace
      query_string = query_string[:-1]
    elif ord(ch) == 13:  # return
      if len(notes.matched_basenames) == 0:
        new_note(query_string)
      else:
        notes.open_selected()
      break
    elif ord(ch) == 27:  # esc code
      ch = getch() # skip the [
      ch = getch()
      if ord(ch) == 66 or ord(ch) == 65: # up/down arrows
        notes.adjust_selection(1 if ord(ch) == 66 else -1)
    else:
      if not first_char_typed:
        query_string = ''
        first_char_typed = True
      query_string += ch

    with open(query_path, 'w') as f:
      f.write(query_string)

if __name__ == '__main__':
  main_loop()
