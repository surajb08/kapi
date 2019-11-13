import unittest
from typing import Tuple

from k8_kat.base.label_set_expressions import LabelSetExpressions

kls = LabelSetExpressions

class TestLabelSetExpressions(unittest.TestCase):

  @property
  def and_tuple(self) -> Tuple:
    return 'app', 'backend'

  @property
  def baked_or_tuple(self) -> Tuple:
    return 'app', ['backend', 'kapi']

  def test_and_to_exp(self):
    self.assertEqual(kls.and_to_exp(self.and_tuple, 'yes'), 'app=backend')
    self.assertEqual(kls.and_to_exp(self.and_tuple, 'no'), 'app!=backend')

  def test_or_set_to_exp(self):
    result = kls.or_set_to_exp(self.baked_or_tuple, 'yes')
    self.assertEqual(result, 'app in (backend, kapi)')

    result = kls.or_set_to_exp(self.baked_or_tuple, 'no')
    self.assertEqual(result, 'app notin (backend, kapi)')

  def test_ands_to_exps(self):
    r1 = kls.ands_to_exps([], 'yes')
    r2 = kls.ands_to_exps([self.and_tuple], 'yes')
    r3 = kls.ands_to_exps([self.and_tuple, self.and_tuple], 'no')

    self.assertEqual(r1, [])
    self.assertEqual(r2, ['app=backend'])
    self.assertEqual(r3, ['app!=backend', 'app!=backend'])

  def test_ors_to_exp(self):
    r1 = kls.ors_to_exp([], 'yes')
    r2 = kls.ors_to_exp([('app', 'one')],  'yes')
    r3 = kls.ors_to_exp([('app', 'one'), ('type', 'two')], 'yes')
    r4 = kls.ors_to_exp([('app', 'one'), ('app', 'two')], 'yes')
    r5 = kls.ors_to_exp([('app', 'one'), ('app', 'two'), ('type', 'three')], 'yes')

    self.assertCountEqual(r1, [])
    self.assertCountEqual(r2, ['app in (one)'])
    self.assertCountEqual(r3, ['app in (one)', 'type in (two)'])
    self.assertCountEqual(r4, ['app in (one, two)'])
    self.assertCountEqual(r5, ['app in (one, two)', 'type in (three)'])

  def test_assemble_expr_lists(self):
    r1 = kls.assemble_expr_lists([])
    r2 = kls.assemble_expr_lists([[]])
    r3 = kls.assemble_expr_lists([['app=backend']])
    r4 = kls.assemble_expr_lists([['app=kapi'], ['app=backend'], []])
    r5 = kls.assemble_expr_lists([['app!=backend'], ['app in (one)']])

    self.assertEqual(r1, '')
    self.assertEqual(r2, '')
    self.assertEqual(r3, 'app=backend')
    self.assertEqual(r4, 'app=kapi,app=backend')
    self.assertEqual(r5, 'app!=backend,app in (one)')

  def test_integration(self):
    r1 = kls.label_conditions_to_expr(
      and_yes_labels=[('debug', 'true'), ('market', 'asia')],
    )

    r2 = kls.label_conditions_to_expr(
      and_yes_labels=[('debug', 'true'), ('market', 'asia')],
      and_no_labels=[('app', 'admin')],
    )

    r3 = kls.label_conditions_to_expr(
      and_no_labels=[('app', 'admin')],
      or_yes_labels=[('kind', 'static'), ('kind', 'electric')]
    )

    r4 = kls.label_conditions_to_expr(
      and_no_labels=[('app', 'admin')],
      or_no_labels=[('geo', 'nkorea')]
    )

    self.assertEqual(r1, 'debug=true,market=asia')
    self.assertEqual(r2, 'debug=true,market=asia,app!=admin')
    self.assertEqual(r3, 'app!=admin,kind in (static, electric)')
    self.assertEqual(r4, 'app!=admin,geo notin (nkorea)')
