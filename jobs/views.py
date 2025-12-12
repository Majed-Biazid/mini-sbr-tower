from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Job
from .serializers import JobReadSerializer, JobListSerializer, JobWriteSerializer
from .filters import JobFilter

class JobViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Job CRUD operations.

    list:       GET /api/jobs/              - List jobs (public)
    create:     POST /api/jobs/             - Create job (company only)
    read:       GET /api/jobs/{id}/         - Get job detail (public)
    update:     PUT /api/jobs/{id}/         - Update job
    delete:     DELETE /api/jobs/{id}/      - Soft delete job
    activate:   POST /api/jobs/{id}/activate/   - Activate job
    deactivate: POST /api/jobs/{id}/deactivate/ - Deactivate job
    """
    queryset = Job.objects.filter(is_active=True)
    filterset_class = JobFilter
    search_fields = ['title', 'description', 'required_skills']
    ordering_fields = ['title', 'created_at', 'salary_min']

    def get_queryset(self):
        # Companies see all their jobs, others see only active
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'company'):
            return Job.objects.filter(company=user.company)
        return Job.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return JobWriteSerializer
        return JobReadSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a job posting"""
        job = self.get_object()
        job.is_active = True
        job.save(update_fields=['is_active'])
        return Response({'message': 'Job activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a job posting"""
        job = self.get_object()
        job.is_active = False
        job.save(update_fields=['is_active'])
        return Response({'message': 'Job deactivated'})

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)