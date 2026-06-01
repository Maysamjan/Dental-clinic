"""Stashes the current request in thread-local storage so model signals can
attribute changes to the acting user and capture their IP."""
import threading

_state = threading.local()


def get_current_request():
    return getattr(_state, "request", None)


def get_current_user():
    request = get_current_request()
    if request and getattr(request, "user", None) and request.user.is_authenticated:
        return request.user
    return None


def get_current_ip():
    request = get_current_request()
    if not request:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR")


class CurrentRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _state.request = request
        try:
            return self.get_response(request)
        finally:
            _state.request = None
