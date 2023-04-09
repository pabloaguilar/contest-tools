from absl import app
from absl import flags
from absl import logging

from auth import Client

from collections import defaultdict
import csv
import libomegaup.omegaup.api as api

FLAGS = flags.FLAGS

flags.DEFINE_string('admin_group', None, 'Grupo de admins para el banco de problemas')
flags.mark_flag_as_required('admin_group')

flags.DEFINE_string('db_problemas', 'db-problemas.csv', 'Nombre del archivo csv a generar con la lista de problemas')
flags.DEFINE_string('posibles_cursos', 'ResolviendoProblemas2022,Reto31312023', 'Alias de los concursos a revisar (como Resolviendo Problemas)')

class DbProblemas(object):
  def __init__(self, omegaup_client):
    self.omegaup_client = omegaup_client
    self.problems = []
    self.concursos = []
    self.usados_en_cursos = defaultdict(list)

  def carga_lista(self):
    problem_api = api.Problem(self.omegaup_client)
    admin_problem_list = problem_api.adminList(page=1, page_size=100)
    self.problems = []
    for problem in admin_problem_list.problems:
      admins = problem_api.admins(problem_alias=problem.alias)
      for admin_group in admins.group_admins:
        if admin_group.alias == FLAGS.admin_group:
          self.problems.append(problem)
          break

  def carga_cursos(self):
    course_api = api.Course(self.omegaup_client)
    for alias in FLAGS.posibles_cursos.split(','):
      logging.info(f'Revisando curso {alias}')
      assignments = course_api.listAssignments(course_alias=alias).assignments
      for assignment in assignments:
        details = course_api.assignmentDetails(course=alias, assignment=assignment.alias)
        for problem in details.problems:
          self.usados_en_cursos[problem.alias].append((alias, assignment.alias, assignment.start_time))

    logging.info(self.usados_en_cursos)

  def genera_csv(self, salida):
    with open(salida, 'w') as f:
      writer = csv.writer(f)
      writer.writerow(['Alias', 'Nombre', 'Link', 'Link a editar', 'Envios', 'Aceptados', 'Usado en', 'Tags'])

      for problem in self.problems:
        print(problem)
        writer.writerow([problem.alias, problem.title, self._link(problem.alias), self._edit_link(problem.alias), problem.submissions, problem.accepted, self._usado(problem.alias), *self._tags(problem)])

  def _link(self, alias):
    return f'https://omegaup.com/arena/problem/{alias}/'

  def _edit_link(self, alias):
    return f'https://omegaup.com/problem/{alias}/edit/'

  def _usado(self, alias):
    return ';'.join(curso[0] for curso in self.usados_en_cursos[alias]) if alias in self.usados_en_cursos else ''

  def _tags(self, problem):
    return [tag.name for tag in problem.tags]


def main(argv):
  del argv  # Unused.

  omegaup_client = Client().omegaup_client
  db_problemas = DbProblemas(omegaup_client)
  db_problemas.carga_cursos()
  db_problemas.carga_lista()
  db_problemas.genera_csv(FLAGS.db_problemas)

if __name__ == '__main__':
  app.run(main)
