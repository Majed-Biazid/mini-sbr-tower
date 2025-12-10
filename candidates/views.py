from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Candidate
from .serializers import CandidateReadSerializer, CandidateWriteSerializer
from .filters import CandidateFilter


class CandidateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Candidate CRUD operations.

    list:   GET /api/candidates/         - List candidates (companies only)
    create: POST /api/candidates/        - Create profile
    read:   GET /api/candidates/{id}/    - Get candidate detail
    update: PUT /api/candidates/{id}/    - Update profile
    delete: DELETE /api/candidates/{id}/ - Soft delete
    me:     GET /api/candidates/me/      - Get current user's profile
    """
    queryset = Candidate.objects.all()
    filterset_class = CandidateFilter
    search_fields = ['full_name', 'bio', 'skills']
    ordering_fields = ['full_name', 'experience_years', 'created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CandidateWriteSerializer
        return CandidateReadSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # Companies can view candidates
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the current user's candidate profile"""
        try:
            candidate = request.user.candidate
            serializer = CandidateReadSerializer(candidate)
            return Response(serializer.data)
        except Candidate.DoesNotExist:
            return Response(
                {'error': 'No candidate profile found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete"""
        instance.soft_delete(user=self.request.user)