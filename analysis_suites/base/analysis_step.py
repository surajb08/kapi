import inflection


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
    print(f"BTW COP KEY " + self.copy_key())
    literal_func = self.copy_tree()[self.copy_key()][key]
    return literal_func(self.copy_bundle())

  def copy_key(self):
    class_name = self.__class__.__name__.replace("Step", '')
    return inflection.underscore(class_name)


  def copy_tree(self):
    return {}
