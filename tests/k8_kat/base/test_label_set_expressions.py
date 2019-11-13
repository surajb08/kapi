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



