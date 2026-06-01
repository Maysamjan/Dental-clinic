"""Consistent API error handling."""
import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def exception_handler(exc, context):
    """Extend DRF's handler to translate Django errors into clean 4xx responses."""
    if isinstance(exc, DjangoValidationError):
        return Response(
            {"detail": exc.messages if hasattr(exc, "messages") else str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    response = drf_exception_handler(exc, context)
    if response is not None:
        return response

    if isinstance(exc, IntegrityError):
        return Response(
            {"detail": "This operation conflicts with existing data."},
            status=status.HTTP_409_CONFLICT,
        )
    if isinstance(exc, Http404):
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    # Unhandled -> log and return a generic 500 (don't leak internals).
    logger.exception("Unhandled API exception", exc_info=exc)
    return Response(
        {"detail": "An unexpected server error occurred."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
