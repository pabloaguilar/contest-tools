from absl import app
from absl import flags
from absl import logging

from auth import Client
from concurso import Concurso, DbConcursos
from participantes import Participantes
from rating import Rating

def main(argv):
  del argv  # Unused.

  omegaup_client = Client().omegaup_client

  db = DbConcursos(omegaup_client)
  db.lee_db()
  db.lee_ranking()

  participantes = Participantes(omegaup_client, None)
  participantes.combina_ranking(db)

if __name__ == '__main__':
  app.run(main)
