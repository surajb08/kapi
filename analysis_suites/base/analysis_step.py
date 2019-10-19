
class AnalysisStep:

  def copy_bundle(self):
    return {}

  def summary_copy(self):
    return self.interpolate_copy('summary')

  def steps_copy(self):
    return self.interpolate_copy('steps')

  def commands_copy(self):
    return self.interpolate_copy('commands')

  def outcome_copy(self):
    return self.interpolate_copy('outcome')

  def interpolate_copy(self, key):
    literal_func = self.copy_tree()[''][key]
    return literal_func(self.copy_bundle())

  def copy_tree(self):
    return {}
