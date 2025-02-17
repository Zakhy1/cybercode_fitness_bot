import pytest
from freezegun import freeze_time

from django.core.files.uploadedfile import SimpleUploadedFile

from bot.core.base import get_main_keyboard
from bot.models.cheque import Cheque
from bot.models.contract import Contract
from bot.models.user_state import UserState


@pytest.fixture
def not_registered_user():
    return UserState.objects.create(chat_id=1)


@pytest.fixture
def registered_user():
    return UserState.objects.create(
        chat_id=1,
        name="Иванов Иван Иванович",
        email="i.ivanov@cybercode.pro",
        confirmation_code="1234",
        is_registered=True
    )


class TestMainKeyboard:
    @pytest.mark.django_db
    def test_not_registered(self, not_registered_user):
        keyboard_for_user = get_main_keyboard(not_registered_user)
        expected_keyboard = {
            "keyboard": [
                [{"text": "Регистрация"}],
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        assert keyboard_for_user == expected_keyboard

    @pytest.mark.django_db
    def test_without_contract_without_cheque(self, registered_user):
        keyboard_for_user = get_main_keyboard(registered_user)
        expected_keyboard = {
            "keyboard": [
                [{"text": "Загрузить договор"}],
                [{"text": "Загрузить чек"}],
                [{"text": "Узнать свой статус"}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        assert keyboard_for_user == expected_keyboard

    @pytest.mark.django_db
    @freeze_time("2025-02-16 12:00:00")
    def test_with_cheque_without_contract(self, registered_user):
        Cheque.objects.create(
            user=registered_user,
            file=SimpleUploadedFile('best_file_eva.pdf',
                                    b'these are the contents of the txt file')
        )
        keyboard_for_user = get_main_keyboard(registered_user)
        expected_keyboard = {
            "keyboard": [
                [{"text": "Загрузить договор"}],
                [{"text": "Загрузить чек (Загружен 16.02.2025)"}],
                [{"text": "Узнать свой статус"}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        assert keyboard_for_user == expected_keyboard

    @pytest.mark.django_db
    @freeze_time("2025-02-16 12:00:00")
    def test_without_cheque_with_contract(self, registered_user):
        Contract.objects.create(
            user=registered_user,
            file=SimpleUploadedFile('best_file_eva.pdf',
                                    b'these are the contents of the txt file')
        )
        keyboard_for_user = get_main_keyboard(registered_user)
        expected_keyboard = {
            "keyboard": [
                [{"text": "Загрузить договор (Загружен 16.02.2025)"}],
                [{"text": "Загрузить чек"}],
                [{"text": "Узнать свой статус"}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        assert keyboard_for_user == expected_keyboard

    @pytest.mark.django_db
    @freeze_time("2025-02-16 12:00:00")
    def test_with_cheque_with_contract(self, registered_user):
        Contract.objects.create(
            user=registered_user,
            file=SimpleUploadedFile('best_file_eva.pdf',
                                    b'these are the contents of the txt file')
        )
        Cheque.objects.create(
            user=registered_user,
            file=SimpleUploadedFile('best_file_eva.pdf',
                                    b'these are the contents of the txt file')
        )
        keyboard_for_user = get_main_keyboard(registered_user)
        expected_keyboard = {
            "keyboard": [
                [{"text": "Загрузить договор (Загружен 16.02.2025)"}],
                [{"text": "Загрузить чек (Загружен 16.02.2025)"}],
                [{"text": "Узнать свой статус"}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        assert keyboard_for_user == expected_keyboard
