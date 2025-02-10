from django.conf import settings


def convert_to_local_time(time_object):
    return time_object.astimezone(settings.TIME_ZONE_OBJECT)
