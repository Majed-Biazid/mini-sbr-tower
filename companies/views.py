from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Company
from .serializers import CompanyReadSerializer, CompanyWriteSerializer
from .filters import CompanyFilter


class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Company CRUD operations.

    list:   GET /api/companies/         - List all companies
    create: POST /api/companies/        - Create company (auth required)
    read:   GET /api/companies/{id}/    - Get company detail
    update: PUT /api/companies/{id}/    - Update company
    delete: DELETE /api/companies/{id}/ - Soft delete company
    me:     GET /api/companies/me/      - Get current user's company
    """
    queryset = Company.objects.all()
    filterset_class = CompanyFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CompanyWriteSerializer
        return CompanyReadSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the current user's company profile"""
        try:
            company = request.user.company
            serializer = CompanyReadSerializer(company)
            return Response(serializer.data)
        except Company.DoesNotExist:
            return Response(
                {'error': 'No company profile found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete"""
        instance.soft_delete(user=self.request.user)