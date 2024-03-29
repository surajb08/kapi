from functools import reduce
from typing import Tuple, List


class LabelLogic:
  @staticmethod
  def and_to_exp(_tuple: Tuple[str, str], eq: bool):
    key, value = _tuple[0], _tuple[1]
    eq_op_sign = "=" if eq else "!="
    return f"{key}{eq_op_sign}{value}"

  @staticmethod
  def or_set_to_exp(_tuple: Tuple[str, List[str]], sign: bool) -> str:
    csv = ', '.join(_tuple[1])
    eq_op = 'in' if sign else 'notin'
    return f"{_tuple[0]} {eq_op} ({csv})"

  @staticmethod
  def ands_to_exps(ands: List[Tuple[str, str]], sign: bool) -> [str]:
    return [LabelLogic.and_to_exp(and_dict, sign) for and_dict in ands]

  @staticmethod
  def ors_to_exp(ors: List[Tuple[str, str]], sign: bool) -> [str]:
    all_keys = [or_tup[0] for or_tup in ors]

    def agg(whole, key) -> Tuple[str, List[str]]:
      match_tups = [tup for tup in ors if tup[0] == key]
      match_values = [tup[1] for tup in match_tups]
      return whole + [(key, match_values)]

    or_sets = reduce(agg, set(all_keys), [])
    return [LabelLogic.or_set_to_exp(or_tup, sign) for or_tup in or_sets]

  @staticmethod
  def assemble_expr_lists(total: List[List[str]]):
    pure = [sub_list for sub_list in total if len(sub_list) > 0]
    macro = [','.join(sub_list) for sub_list in pure]
    return ','.join(macro)

  @staticmethod
  def partition_tups(tups: List[Tuple[str, str]]):
    keys = [t[0] for t in tups]
    repeating_keys = set([k for k in keys if keys.count(k) > 1])
    equalities = [t for t in tups if t[0] not in repeating_keys]
    sets = [t for t in tups if t[0] in repeating_keys]
    return [equalities, sets]

  @staticmethod
  def label_conditions_to_expr(inc_tups, exc_tups) -> str:
    inc_eqs, inc_sets = LabelLogic.partition_tups(inc_tups)
    exc_eqs, exc_sets = LabelLogic.partition_tups(exc_tups)

    strict_incs = LabelLogic.ands_to_exps(inc_eqs, True)
    set_incs = LabelLogic.ors_to_exp(inc_sets, True)

    strict_excs = LabelLogic.ands_to_exps(exc_eqs, False)
    set_excs = LabelLogic.ors_to_exp(exc_sets, False)

    return LabelLogic.assemble_expr_lists([
      strict_incs,
      set_incs,
      strict_excs,
      set_excs
    ])

