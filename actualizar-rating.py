from absl import app
from absl import flags
from absl import logging

import csv
import pandas as pd

from typing import Dict, List, Tuple
from unidecode import unidecode

from auth import Client
from concurso import Concurso, DbConcursos
from participantes import Participante, Participantes
from rating import CodeforcesRatingCalculator, StandingsRow

def aplicar_cambios(rating: Dict[Participante, int], cambios: Dict[Participante, int]) -> Dict[Participante, Tuple[int,int]]:
  for participante, cambio in cambios.items():
    if participante in rating:
      rating[participante] = (round(rating[participante][0] + cambio), rating[participante][1] + 1)
    else:
      rating[participante] = (round(CodeforcesRatingCalculator.INITIAL_RATING + cambio), 1)
  return rating

def genera_standings(participantes: Participantes, ranking: pd.DataFrame) -> List[StandingsRow]:
  standings = []
  print(ranking.head())
  for _, row in ranking.iterrows():
    if not row['tiene_envios']:
      continue
    participante = participantes.participantes[participantes.alias_db.nombre_canonico(unidecode(row['nombre']))]
    standings.append(StandingsRow(row['rank'], row['puntos'], participante))
  return standings

def calcula_rating(db: DbConcursos,
                   participantes: Participantes,
                   calculadora: CodeforcesRatingCalculator) -> Dict[Participante, int]:
  rating: Dict[Participante, int] = {}
  for concurso in db.concursos:
    cambios = calculadora.calculateRatingChanges(rating, genera_standings(participantes, concurso.ranking))
    rating = aplicar_cambios(rating, cambios)
  # aplicar_rating(rating, participantes)
  return rating

def main(argv):
  del argv  # Unused.

  omegaup_client = Client().omegaup_client

  db = DbConcursos(omegaup_client)
  db.lee_db()
  db.lee_ranking()

  participantes = Participantes(omegaup_client, None)
  participantes.combina_ranking(db)

  rating_calculator = CodeforcesRatingCalculator()
  nuevo_rating = calcula_rating(db, participantes, rating_calculator)

  rating_en_orden = sorted(nuevo_rating.items(), key=lambda row: row[1], reverse=True)
  with open('rating.csv', 'w') as salida:
    writer = csv.writer(salida)
    for participante, rating in rating_en_orden:
      writer.writerow([participante.nombre, *rating])


if __name__ == '__main__':
  app.run(main)
