from absl import flags

import libomegaup.omegaup.api as api

FLAGS = flags.FLAGS

flags.DEFINE_string('omegaup_token', None, 'Token para la API omegaUp')
flags.mark_flag_as_required('omegaup_token')

class Client(object):
  def __init__(self):
    self.omegaup_client = api.Client(api_token=FLAGS.omegaup_token)

  @classmethod
  def validate_token(cls, token):
    pass