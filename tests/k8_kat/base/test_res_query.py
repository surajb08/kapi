import unittest

from k8_kat.base.res_query import ResQuery


class TestResQuery(unittest.TestCase):

  def setUp(self) -> None:
    self.subject = ResQuery(None, None)

  def test_is_single_ns(self):
    self.subject.update(in_ns=['default'])
    self.assertTrue(self.subject.is_single_ns())

    self.subject.update(in_ns=['default', 'dev'])
    self.assertFalse(self.subject.is_single_ns())

  def test_has_lb_any_filters(self):
    result = self.subject.gen_server_label_selector()
    self.assertEqual(result, '')

    self.subject.update(
      lbs_inc_each=[('app', 'backend')],
      lbs_exc_each=[('debug', 'false')]
    )
    result = self.subject.gen_server_label_selector()
    self.assertNotEqual(result, '')

    self.subject.update(
      lbs_inc_each=[('app', 'backend')],
      lbs_exc_each=[('debug', 'false')],
      lbs_exc_any=[('v', '1')],
    )
    result = self.subject.gen_server_label_selector()
    self.assertEqual(result, '')


if __name__ == '__main__':
    unittest.main()
