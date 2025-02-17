from bot.validators.validate_name import validate_name


class TestUserName:
    def test_correct(self):
        value = validate_name("Иванов Иван Иванович")
        assert value is True

        value = validate_name("Иванов Иван")
        assert value is True

        value = validate_name("Иванов Иван Иванович")
        assert value is True

        value = validate_name("Иванов-Петров Иван")
        assert value is True

    def test_incorrect(self):
        value = validate_name("Иванов")
        assert value is False

        value = validate_name("Иванов Иван Иван Иван")
        assert value is False
