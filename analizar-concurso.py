import csv
import re
import sys

from absl import app
from absl import flags
from absl import logging

FLAGS = flags.FLAGS

flags.DEFINE_string('name', 'Jane Random', 'Your name.')

def main(argv):
  del argv  # Unused.

  print('Running under Python {0[0]}.{0[1]}.{0[2]}'.format(sys.version_info),
        file=sys.stderr)
  logging.info('echo is %s.', FLAGS.name)


if __name__ == '__main__':
  app.run(main)