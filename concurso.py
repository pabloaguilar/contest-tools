from absl import flags
from absl import logging

import os
import pickle
from datetime import datetime
from typing import List, Optional

import pandas as pd

import libomegaup.omegaup.api as api

GRUPO_PROBLEMSETTERS = 'Problem-setters-MP'

FLAGS = flags.FLAGS

flags.DEFINE_string('db_concursos', None, 'Archivo CSV con la tabla de concursos')
flags.DEFINE_string('cache_concursos', 'cache', 'Directorio para guardar el cache de concursos')

class Concurso(object):
  def __init__(self, omegaup_client, alias):
    self.omegaup_client = omegaup_client
    self.alias = alias
    self.contest_api = api.Contest(omegaup_client)
    self.scoreboard = None
    self.ranking = None
    self.finish_time = None
    
  @classmethod
  def _archivo_cache(cls, alias):
    return os.path.join(os.getcwd(), FLAGS.cache_concursos, alias + '.pickle')

  def tal_vez_guarda_cache(self):
    if self.finish_time is not None and self.finish_time <= datetime.now():
      cache_path = self._archivo_cache(self.alias)
      with open(cache_path, 'wb') as cache_file:
        pickle.dump(self, cache_file)

  def crear(self):
    try:
      self.contest_api.details(contest_alias=self.alias)
    except Exception as e:
      errorname = e.args[0]['errorname']
      if errorname == 'loginRequired':
        logging.error('El token no es correcto')
        raise
      elif errorname == 'contestNotFound':
        logging.info('El concurso %d no existe, intentando crearlo', self.alias)
        self._crear_realmente()
    self._configurar_concurso()

  def _configurar_concurso(self):
    # @omegaup-request-param mixed $admission_mode
    # @omegaup-request-param mixed $alias
    # @omegaup-request-param mixed $description
    # @omegaup-request-param mixed $feedback
    # @omegaup-request-param mixed $finish_time
    # @omegaup-request-param mixed $languages
    # @omegaup-request-param bool|null $needs_basic_information
    # @omegaup-request-param null|string $problems
    # @omegaup-request-param mixed $scoreboard
    # @omegaup-request-param null|string $score_mode
    # @omegaup-request-param mixed $show_scoreboard_after
    # @omegaup-request-param mixed $start_time
    # @omegaup-request-param mixed $submissions_gap
    # @omegaup-request-param null|string $teams_group_alias
    # @omegaup-request-param mixed $title
    pass

  def _crear_realmente(self):
    self.contest_api.create(alias=self.alias,
        finish_time=None)

  def agregar_admins(self):
    self.contest_api.addGroupAdmin(contest_alias=self.alias,
                                   group=GRUPO_PROBLEMSETTERS)

  def actualizar_participantes(self, participantes):
    participantes.apply(lambda row: None, axis=1)
    self.contest_api.addUser(contest_alias=self.alias, usernameOrEmail='')

  @classmethod
  def _extrae_datos(cls, renglon):
    return {'usuario': renglon.username,
            'nombre': renglon.name,
            'puntos': renglon.total.points,
            'rank': renglon.place,
            'tiene_envios': any(problem.runs > 0 for problem in renglon.problems)}

  def lee_ranking(self):
    if self.scoreboard is None:
      try:
        self.scoreboard = self.contest_api.scoreboard(contest_alias=self.alias)
      except Exception as e:
        logging.error("No se pudo descargar scoreboard: %s", e)
      if self.scoreboard is None:
        logging.error('No se pudo cargar scoreboard de %s', self.alias)
        return
      self.ranking = pd.DataFrame(
          self._extrae_datos(renglon) for renglon in self.scoreboard.ranking)
      self.finish_time = self.scoreboard.finish_time
    else:
      logging.vlog(2, 'El scoreboard de %s ya se habia cargado', self.alias)

    logging.info('Ranking de %s, termina en %s', self.alias, self.finish_time)
    logging.vlog(2, self.ranking)

class DbConcursos(object):
  def __init__(self, omegaup_client):
    self.omegaup_client = omegaup_client
    self.db: Optional[pd.DataFrame] = None
    self.concursos: Optional[pd.Series[Concurso]] = None

  def lee_db(self):
    self.db = pd.read_csv(FLAGS.db_concursos)
    logging.vlog(2, self.db)

    self.concursos = self.db.apply(
        lambda row: self.carga_concurso(row['alias']), axis=1)
    logging.vlog(2, self.concursos)

  def carga_concurso(self, alias: str) -> Concurso:
    cache_path = Concurso._archivo_cache(alias)
    concurso: Concurso = None

    try:
      if os.path.exists(cache_path):
        with open(cache_path, 'rb') as cache_file:
          concurso = pickle.load(cache_file)
          logging.info(2, 'Cargando concurso %s del cache', alias)
    except:
      pass

    if concurso is None:
      try:
        concurso = Concurso(self.omegaup_client, alias)
        logging.info('Cargando concurso %s de la API', alias)
      except:
        logging.error('No se pudo cargar concurso %s de la API', alias)

    return concurso

  def lee_ranking(self):
    self.concursos.apply(lambda concurso: concurso.lee_ranking())
    self.concursos.apply(lambda concurso: concurso.tal_vez_guarda_cache())
