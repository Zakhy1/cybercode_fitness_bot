import functools
import traceback

from django.http import HttpResponse

from project.logging_settings import error_logger


def base_view(fn):
    @functools.wraps(fn)
    def inner(request, *args, **kwargs):
        try:
            return fn(request, *args, **kwargs)
        except Exception as e:
            error_logger.error(traceback.format_exc())
            return HttpResponse(status=500, content="error occurred")

    return inner
