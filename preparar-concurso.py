from absl import app
from absl import flags
from absl import logging

import auth
from participantes import Participantes
from concurso import Concurso
from plantilla import Plantilla

FLAGS = flags.FLAGS

flags.DEFINE_string('alias', None, 'Alias del concurso que manejar')
flags.DEFINE_string('id_hoja_registro', None, 'ID en Drive de la hoja de registro')
flags.mark_flag_as_required('id_hoja_registro')
flags.DEFINE_bool('enviar_correo', False, 'Si se usa esta bandera, se envia el correo las participantes')

def main(argv):
  del argv  # Unused.
  logging.info('Administrando el concurso %s.', FLAGS.alias)

  omegaup_client = auth.Client().omegaup_client
  
  participantes = Participantes(omegaup_client, FLAGS.id_hoja_registro)
  # participantes.asigna_uuids()
  # participantes.crea_identidades()

  concurso = Concurso(omegaup_client, FLAGS.alias)
  concurso.crear()
  concurso.agregar_admins()
  concurso.actualizar_participantes(participantes)

  if FLAGS.enviar_correo:
    participantes.enviar_correo(Plantilla())

if __name__ == '__main__':
  app.run(main)