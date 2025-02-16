import unittest

from bot.validators.is_corporate_email import is_corporate_email


class CorporateEmailTestCase(unittest.TestCase):
    def test_correct(self):
        value = is_corporate_email("z.lyrshikov@cybercode.pro")
        self.assertEqual(value, True)

        value = is_corporate_email("a.pichugin@cybercode.pro")
        self.assertEqual(value, True)

        value = is_corporate_email("d.krivosheev@cybercode.pro")
        self.assertEqual(value, True)

        value = is_corporate_email("d.shibert@cybercode.pro")
        self.assertEqual(value, True)

        value = is_corporate_email("r.gartman@cybercode.pro")
        self.assertEqual(value, True)

    def test_incorrect(self):
        value = is_corporate_email("z.lyrshikov@cyberocode.pro")
        self.assertEqual(value, False)

        value = is_corporate_email("@cybercode.pro")
        self.assertEqual(value, False)

        value = is_corporate_email("d.krivosheev@gmail.pro")
        self.assertEqual(value, False)

        value = is_corporate_email("d.shibert@cybercode")
        self.assertEqual(value, False)


if __name__ == '__main__':
    unittest.main()
