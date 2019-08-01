#!/usr/bin/env python

"""
This tools is released under GNU GPL v3
Author: Cyril DELETRE (@kotzebuedog)
"""


from os.path import basename,getsize,splitext
from sys import stderr, stdout
import argparse



BLACK = u'\u001b[30m'
RED = u'\u001b[31m'
GREEN = u'\u001b[32m'
YELLOW = u'\u001b[33m'
BLUE = u'\u001b[34m'
MAGENTA = u'\u001b[35m'
CYAN  = u'\u001b[36m'
WHITE = u'\u001b[37m'
RESET = u'\u001b[0m'

MAX_FILESIZE = 100 * pow(1024,3) # 100 MB

def pinfo(text):
  stderr.write(GREEN)
  stderr.write(text)
  stderr.write(RESET)
  stderr.write('\n')
  stderr.flush()


def pverbose(text, level=1):
  if level <= args.verbose:
    stdout.write(text)
    stdout.write('\n')
    stdout.flush()

def pwarning(text):
  stderr.write(YELLOW)
  stderr.write(text)
  stderr.write(RESET)
  stderr.write('\n')
  stderr.flush()

def perror(text, quit=1):
  stderr.write(RED)
  stderr.write(text)
  stderr.write(RESET)
  stderr.write('\n')
  stderr.flush()

  if quit != 0:
    exit(quit)
  

parser = argparse.ArgumentParser(description='IQ file scissors')

parser.add_argument('iq_file', type=argparse.FileType('rb'), metavar='IQ-FILE',
                    help='IQ filepath')

parser.add_argument('-s', '--start', metavar='START',
                    help='Start cursor in second (suffix with m for ms)')

parser.add_argument('-e', '--end', metavar='END',
                    help='End cursor in second (suffix with m for ms)')

parser.add_argument('-d', '--duration', metavar='DURATION', 
                    help='Duration in second (suffix with m for ms)')

parser.add_argument('-R','--sample-rate', metavar='SAMPLE-RATE',
                    help='Sample rate (sps)')

parser.add_argument('-S','--sample-size', metavar='SAMPLE-SIZE',
                    help='Sample size (bytes)')

parser.add_argument('-a', '--auto-detect', action='store_true', default=False,
                    help='Try to autodetect file format')

parser.add_argument('-f', '--force', action='store_true', default=False,
                    help='Ignore file size warning and copy anyway')

parser.add_argument('-v', '--verbose', action='count', default=0,
                    help='Incrase verbosity level')

args = parser.parse_args()

filename=basename(args.iq_file.name)
duration=0

if args.auto_detect:
  if filename.startswith('gqrx_'):
    pverbose('GQRX file found',1)
    # try split on the filename
    tab_filename = filename.split('_')
    if len(tab_filename) > 5:
      pinfo('Supported GQRX file found')
      pverbose('Filename pattern supported',2)
      args.sample_rate = tab_filename[4]
      args.sample_size = 8
      pinfo('Detected I+Q sample rate: %s sps' % args.sample_rate)
      pinfo('Detected I+Q sample size: %s B' % args.sample_size)
    else:
      pverbose('Unsupported filename pattern',2)
      perror('Cannot auto-detect file format')
  else:
    pverbose('No clue found in filename',1)
    perror('Cannot auto-detect file format')


filesize = getsize(filename)
pinfo('IQ file size: %d kB' % ( filesize / 1024 ) )

file_bitrate = int(args.sample_rate) * int(args.sample_size)
pinfo('IQ file bitrate: %d kB/s' % (file_bitrate / 1024))

file_duration = 1000 * filesize / file_bitrate
pinfo('IQ file duration: %d ms' % file_duration)



if None not in [args.start, args.end, args.duration]:
  perror('You can only give two parameters amongst start, end and duration')

if args.start is None:
  pverbose('No start cursor given')
  start = 0
elif args.start[-1] == 'm':
  start = int(args.start[:-1])
else:
  start = int(args.start) * 1000   

if start > file_duration:
  perror('The specified start cursor (%d ms) is out of the file duration (%d ms)' % (start, file_duration))

if args.end is None:
  pverbose('No end cursor given')
  end = 0
elif args.end[-1] == 'm':
  end = int(args.end[:-1])
else:
  end = int(args.end) * 1000   

if args.duration is None:
  pverbose('No duration given')
  duration = end - start
else:
  if args.duration[-1] == 'm':
    duration = int(args.duration[:-1])
  else:
    duration = int(args.duration) * 1000 

  if end > 0:
    start = end - duration
  else:
    end = start + duration

if start + duration > file_duration:
  pwarning('The specified duration overlaps the end of the file. Ignoring it')
  duration = file_duration - start
  end = file_duration

data_length = (duration * file_bitrate) / 1000

filecut_path = splitext(args.iq_file.name)[0]
filecut_path += '_CUT'
filecut_path += '_%d-%dms' % (start,end)
filecut_path += splitext(args.iq_file.name)[1]

pverbose('Will copy data to %s' % filecut_path)

pinfo('%d ms of data (%d kB) will be copied' % ( duration, data_length / 1024 ) )

if data_length > MAX_FILESIZE:
  if not args.force:
    perror('Data length (%d MB) bigger than the limit (%d MB)' % ( (data_length / pow(1024,2)), (MAX_FILESIZE/pow(1024,2)) ), 0)
    dd_cmd = 'dd bs='
    dd_cmd += str(file_bitrate / 1000)
    dd_cmd += ' skip='
    dd_cmd += str(start)
    dd_cmd += ' count='
    dd_cmd +=  str(duration)
    dd_cmd += ' if=\''
    dd_cmd += args.iq_file.name
    dd_cmd += '\' of=\''
    dd_cmd += filecut_path
    dd_cmd += '\''

    pwarning('Use dd command instead: %s' % dd_cmd)
    perror('Or use --force to ignore the limit')
  else:
    pwarning('Using force mode to copy %d MB of data' % (data_length / pow(1024,2)))

pverbose('Copying data')
iq_filecut = open(filecut_path,'w+')
args.iq_file.seek( (start * file_bitrate) / 1000 )
iq_filecut.write( args.iq_file.read( (duration * file_bitrate) / 1000 ) )

iq_filecut.close()
args.iq_file.close()
pverbose('Copy done')

pinfo('Data copied to %s' % filecut_path)
