import unittest

from utils.tools import BasicTools


class TestBasicTools(unittest.TestCase):

    def setUp(self):
        self.tools = BasicTools()
    
    def test_check_appeals_number(self):
        self.assertTrue(self.tools.check_appeals_number('123, 1243214, 132, 1'))
        self.assertTrue(self.tools.check_appeals_number('2314 3214231 2134 12'))
        self.assertTrue(self.tools.check_appeals_number('23$3214"231?2134.12'))
        self.assertFalse(self.tools.check_appeals_number('awhgaewh'))
        self.assertFalse(self.tools.check_appeals_number('54 54wsg 5466 0644'))
        self.assertIsInstance(self.tools.check_appeals_number('927 456-12_34'), bool)

    def test_format_appeals_number(self):
        self.assertEqual(self.tools.format_appeals_number('123, 1243214, 132, 1'), '123 1243214 132 1')
        self.assertTrue(self.tools.format_appeals_number('23$3214"231?2134.12'), '23 3214 231 2134 12')
        self.assertIsInstance(self.tools.format_appeals_number('123, 1243214, 132, 1'), str)
        with self.assertRaises(TypeError):
            self.tools.format_appeals_number(846461651)
            self.tools.format_appeals_number(None)
            self.tools.format_appeals_number(True)

    def test_check_phone_number(self):
        self.assertTrue(self.tools.check_phone_number('7 (123)-456-78-90'))
        self.assertTrue(self.tools.check_phone_number('927 456-12_34'))
        self.assertFalse(self.tools.check_phone_number('awhgaewh'))
        self.assertFalse(self.tools.check_phone_number('1235ffqwf12'))
        self.assertFalse(self.tools.check_phone_number('3 456 78 90'))
        self.assertIsInstance(self.tools.check_phone_number('927 456-12_34'), bool)
        with self.assertRaises(TypeError):
            self.tools.check_phone_number(846461651)
            self.tools.check_phone_number(None)
            self.tools.check_phone_number(True)

    def test_format_phone_number(self):
        self.assertEqual(self.tools.format_phone_number('7 (123)-456-78-90'), '7 123 456 78 90')
        self.assertEqual(self.tools.format_phone_number('927 456-12_34'), '927 456 12 34')
        self.assertEqual(self.tools.format_phone_number('Нет номера'), 'Нет номера')
        self.assertIsInstance(self.tools.format_phone_number('927 456-12_34'), str)
        with self.assertRaises(TypeError):
            self.tools.check_phone_number(846461651)
            self.tools.check_phone_number(None)
            self.tools.check_phone_number(True)

    def test_ending_of_word(self):
        self.assertEqual(self.tools.ending_of_word(21), 'обращение')
        self.assertEqual(self.tools.ending_of_word(10), 'обращений')
        self.assertEqual(self.tools.ending_of_word(3), 'обращения')
        self.assertIsInstance(self.tools.ending_of_word(150), str)
        with self.assertRaises(TypeError):
            self.tools.check_phone_number('wsggewrhrwe')
            self.tools.check_phone_number(None)
            self.tools.check_phone_number(True)

if __name__ == '__main__':
    unittest.main()