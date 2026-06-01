from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import user_has_perm
from apps.core.pdf import build_pdf
from .excel import build_xlsx
from .services import REPORTS


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def report(request, name):
    """
    Generic report endpoint:
      GET /api/reports/<name>/?from=&to=&format=json|pdf|excel
    """
    if not user_has_perm(request.user, "reports.view"):
        return Response({"detail": "Permission denied."}, status=403)

    builder = REPORTS.get(name)
    if not builder:
        return Response({"detail": "Unknown report"}, status=404)

    title, header, rows, summary = builder(request.query_params)
    fmt = request.query_params.get("format", "json")

    if fmt == "pdf":
        pdf = build_pdf(title, summary, header, rows)
        resp = HttpResponse(pdf, content_type="application/pdf")
        resp["Content-Disposition"] = f'inline; filename="{name}.pdf"'
        return resp

    if fmt in ("excel", "xlsx"):
        xlsx = build_xlsx(title, header, rows)
        resp = HttpResponse(
            xlsx,
            content_type="application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet",
        )
        resp["Content-Disposition"] = f'attachment; filename="{name}.xlsx"'
        return resp

    return Response(
        {"title": title, "header": header, "rows": rows, "summary": summary}
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def report_index(request):
    if not user_has_perm(request.user, "reports.view"):
        return Response({"detail": "Permission denied."}, status=403)
    return Response({"available": sorted(REPORTS.keys())})
