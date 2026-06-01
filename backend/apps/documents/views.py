from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser

from apps.core.permissions import HasModulePermission
from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    module = "documents"
    permission_classes = [HasModulePermission]
    parser_classes = [MultiPartParser, FormParser]
    queryset = Document.objects.select_related("patient")
    serializer_class = DocumentSerializer
    filterset_fields = ["patient", "type"]

    def perform_create(self, serializer):
        serializer.save(
            uploaded_by=self.request.user if self.request.user.is_authenticated else None
        )
