from bot.models.cheque import Cheque
from bot.models.circle import Circle
from bot.models.contract import Contract
from bot.models.user_state import UserState
from settings.models import Settings

months_names = {
    '01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель',
    '05': 'Май', '06': 'Июнь', '07': 'Июль', '08': 'Август',
    '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'
}


class ReportService:
    def generate_report(self, start_date, end_date):
        required_count = int(
            Settings.get_setting("circle_required_count", "4")
        )
        host_url = Settings.get_setting("HOST_URL", "http://localhost:8000")
        params = {
            'required_count': required_count,
            'host_url': host_url
        }
        report = {"accessed": [], "not_accessed": []}

        users = UserState.objects.filter(banned=False)

        for user in users:
            user_dict, accessed = self.check_user(user, start_date, end_date,
                                                  params)
            if user_dict == {} and accessed is False:
                continue
            if accessed:
                report['accessed'].append(user_dict)
            else:
                report['not_accessed'].append(user_dict)

        return report

    def check_user(self, user, start_date, end_date, params) -> tuple[
        dict, bool]:
        required_count = params['required_count']
        host_url = params['host_url']

        reasons = []

        if not user.is_registered:
            if user.name is None:
                return {}, False

        user_has_contract = Contract.objects.filter(user=user).exists()
        if not user_has_contract:
            reasons.append('Не отправил договор')

        user_circles_count = Circle.objects.filter(
            uploaded_at__gte=start_date,
            uploaded_at__lte=end_date,
            user=user).count()

        if user_circles_count < required_count:
            reasons.append(
                f'Недостаточное количество посещений ({user_circles_count}/{required_count})')

        cheques = Cheque.objects.filter(
            user=user,
            uploaded_at__gte=start_date,
            uploaded_at__lte=end_date
        )

        if not cheques.exists():
            existent_cheque = Cheque.objects.filter(user=user).order_by(
                "uploaded_at").last()
            if existent_cheque is not None:
                reasons.append(f"Нет чека за период: последний чек от "
                               f"{existent_cheque.uploaded_at.strftime('%d.%m.%Y')}")
            else:
                reasons.append('Нет чека за период')

        cheques_by_month = {}
        for cheque in cheques:
            month_key = cheque.uploaded_at.strftime('%Y-%m')
            if month_key not in cheques_by_month or \
                    cheque.uploaded_at > cheques_by_month[month_key].uploaded_at:
                cheques_by_month[month_key] = cheque

        latest_contract = Contract.objects.filter(user=user).order_by(
            'uploaded_at').last()

        user_dict = {
            "id": user.id,
            "name": user.get_name(),
            "visits_count": user_circles_count,
            "contract": f'{host_url}{latest_contract.file.url}' if user_has_contract else None,
            "cheques": [
                {
                    "month": f"{months_names[cheque.uploaded_at.strftime('%m')]} "
                             f"{cheque.uploaded_at.strftime('%Y')}",
                    "url": f'{host_url}{cheque.file.url}'
                }
                for cheque in cheques_by_month.values()
            ],
            'reasons': reasons
        }
        accessed = True if len(reasons) == 0 else False
        return user_dict, accessed
