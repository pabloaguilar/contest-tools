import uuid
from typing import Optional

import gspread
import pandas as pd

from absl import logging
from concurso import DbConcursos

import libomegaup.omegaup.api as api

class Participantes(object):
  def __init__(self, omegaup_client: api.Client, id_hoja_registro: Optional[str]):
    self.omegaup_client = omegaup_client
    self.id_hoja_registro = id_hoja_registro    
    self.data = None
    # self.lee_registro()

  def lee_registro(self):
    sheets = gspread.service_account()
    hoja = sheets.open_by_key(self.id_hoja_registro).get_worksheet(0)
    self.data = pd.DataFrame(hoja.get_all_records())

  def asigna_uuids(self):
    assert self.data is not None
    if 'uuid' in self.data:
      logging.info('Llenando %d UUIDs faltantes', self.data['uuid'].isna().count())
    else:
      logging.info('Creando uuids desde cero')
      self.data['uuid'] = None

    uuids_faltantes = self.data['uuid'].isna()
    self.data['uuid'][uuids_faltantes] = (
        self.data[uuids_faltantes].apply(lambda _: uuid.uuid4(), axis=1))
    self._sube_datos()

  def crea_identidades(self):
    assert self.data is not None
    if 'identidad' in self.data:
      logging.info('Llenando identidades faltantes')
    else:
      logging.info('Creando identidades desde cero')
      self.data['identidad'] = None
    identidades_faltantes = self.data['identidad'].isna()
    logging.info('Agregando %d identidades faltantes', identidades_faltantes.count())

    # TODO: Generar nuevas identidades que no esten incluidas en las anteriores
    identity_api = api.Identity(self.omegaup_client)
    # group_alias
    # json_encode([ country_id: string,
    #   gender: string,
    #   name: string,
    #   password: string,
    #   school_name: string,
    #   state_id: string,
    #   username: string
    # ])
    #identity_api.bulkCreate()
    self._sube_datos()

  def enviar_correo(self, plantilla):
    logging.info('Enviando correos a %d participantes', len(self.data))
    self.data.apply(
        lambda row: self._enviar_correo(
            plantilla, row, enviar_realmente=False), axis=1)

    enviar_realmente = input('Enviar realmente [y/N]?')
    if enviar_realmente == 'y':
      self.data.apply(
          lambda row: self._enviar_correo(
              plantilla, row, enviar_realmente=True), axis=1)

  def combina_ranking(self, db: DbConcursos):
    pass

  def _sube_datos(self):
    sheets = gspread.service_account()
    hoja = sheets.open_by_key(self.id_hoja_registro).get_worksheet(0)
    hoja.update([self.data.columns.values.tolist()] + self.data.values.tolist())

  def _enviar_correo(self, plantilla, datos: pd.Series, enviar_realmente: bool):
    logging.info('%s Enviando correo a %s', 'Realmente' if enviar_realmente else '', datos)
    contenido = plantilla.personalizar(datos)
    logging.vlog(2, contenido)