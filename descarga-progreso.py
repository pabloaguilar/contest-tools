from absl import app
from absl import flags
from absl import logging

import pandas as pd

from typing import Dict, List, Tuple
from unidecode import unidecode

from auth import Client
from libomegaup.omegaup.api import Course

FLAGS = flags.FLAGS
flags.DEFINE_string('curso', 'ResolviendoProblemas2021', 'Alias del curso')

def convierte_a_renglon(progreso):
  rv = {'username': progreso.username}
  for a, v in progreso.assignments.items():
    rv[a] = v.progress
  return rv

def main(argv):
  del argv  # Unused.

  omegaup_client = Client().omegaup_client
  course = Course(omegaup_client)
  page = 1
  alumnos = []
  while page is not None:
    logging.info(f'Fetching page {page}')
    progress = course.studentsProgress(
      course=FLAGS.curso,
      page=page,
      length=100)
    logging.info(f'Got entries: {len(progress.progress)}')
    page = progress.nextPage
    alumnos.extend(convierte_a_renglon(p) for p in progress.progress)

  df = pd.DataFrame(alumnos)
  df.to_csv('progreso.csv', index=False)

if __name__ == '__main__':
  app.run(main)
