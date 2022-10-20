import collections
import sys
import typing

from libomegaup.omegaup import api


COURSE_ALIAS = 'ResolviendoProblemas2021'

def main():
  with open('omegaup.api.token', 'r') as f:
    token = f.read().strip()
  client = api.Client(api_token=token)
  course = api.Course(client)
  assignments = course.listAssignments(course_alias=COURSE_ALIAS)
  
  languages = collections.Counter()
  for assignment in assignments['assignments']:
    runs = course.runs(course_alias=COURSE_ALIAS, assignment_alias=assignment['alias'])
    languages.update(run['language'] for run in runs['runs'])

  print(languages)

if __name__ == '__main__':
  main()