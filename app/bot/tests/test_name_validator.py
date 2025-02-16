import unittest

from bot.validators.validate_name import validate_name


class UserNameTestCase(unittest.TestCase):
    def test_correct(self):
        value = validate_name("Иванов Иван Иванович")
        self.assertEqual(value, True)

        value = validate_name("Иванов Иван")
        self.assertEqual(value, True)

        value = validate_name("Иванов Иван Иванович")
        self.assertEqual(value, True)

        value = validate_name("Иванов-Петров Иван")
        self.assertEqual(value, True)

    def test_incorrect(self):
        value = validate_name("Иванов")
        self.assertEqual(value, False)

        value = validate_name("Иванов Иван Иван Иван")
        self.assertEqual(value, False)
