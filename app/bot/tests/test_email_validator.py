import unittest

from bot.validators.is_corporate_email import is_corporate_email


class TestCorporateEmail:
    def test_correct(self):
        value = is_corporate_email("z.lyrshikov@cybercode.pro")
        assert value is True

        value = is_corporate_email("a.pichugin@cybercode.pro")
        assert value is True

        value = is_corporate_email("d.krivosheev@cybercode.pro")
        assert value is True

        value = is_corporate_email("d.shibert@cybercode.pro")
        assert value is True

        value = is_corporate_email("r.gartman@cybercode.pro")
        assert value is True

    def test_incorrect(self):
        value = is_corporate_email("z.lyrshikov@cyberocode.pro")
        assert value is False

        value = is_corporate_email("@cybercode.pro")
        assert value is False

        value = is_corporate_email("d.krivosheev@gmail.pro")
        assert value is False

        value = is_corporate_email("d.shibert@cybercode")
        assert value is False
