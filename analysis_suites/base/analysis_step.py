import inflection


class AnalysisStep:

  def __init__(self):
    self.outcome = None
    self.outcomes_bundle = {}
    self.outputs = []

  def as_positive(self, outputs, bundle):
    self.record_step_performed(True, outputs, bundle)

  def as_negative(self, outputs, bundle):
    self.record_step_performed(False, outputs, bundle)

  def record_step_performed(self, outcome, outputs, bundle):
    self.outcome = outcome
    self.outputs = outputs
    self.outcomes_bundle = bundle

  def copy_bundle(self):
    return {
      **self._copy_bundle(),
      **self.outcomes_bundle
    }

  def summary_copy(self):
    return self.interpolate_copy('summary')

  def steps_copy(self):
    return self.interpolate_copy('steps')

  def commands_copy(self):
    return self.interpolate_copy('commands')

  def outcome_copy(self):
    return self.interpolate_copy('outcome')

  def interpolate_copy(self, key):
    literal_func = self.load_copy_tree()[self.copy_key()][key]
    return literal_func(self.copy_bundle())

  def copy_key(self):
    class_name = self.__class__.__name__.replace("Step", '')
    return inflection.underscore(class_name)

  def load_copy_tree(self):
    return {}

  def perform(self):
    pass

  def _copy_bundle(self):
    return {}

