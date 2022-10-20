import jinja2
import pandas as pd

from absl import flags

FLAGS = flags.FLAGS

flags.DEFINE_string('plantilla', None, 'La plantilla a usar para enviar correos')

class Plantilla(object):
  def __init__(self):
    if FLAGS.plantilla is None:
      raise ValueError('Se debe especificar que plantilla usar, p.ejem: --plantilla=correo.html')

    loader = jinja2.FileSystemLoader(searchpath="./templates")
    env = jinja2.Environment(loader=loader, autoescape=True)
    self.template = env.get_template(FLAGS.plantilla)

  def personalizar(self, datos: pd.DataFrame):
    return self.template.render(datos)