from django.db.models import Sum
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Farm
from .serializers import FarmSerializer


class DashboardView(APIView):
    """GET /api/dashboard/ (optional ?farm=<id>) — everything the home screen
    needs in one request: counts across the user's farms plus budget totals."""
    def get(self, request):
        from crops.models import Crop, Plant
        from tasks.models import Task
        from budgeting.models import Transaction

        farms = Farm.objects.filter(owner=request.user)
        farm = request.query_params.get('farm')
        if farm:
            farms = farms.filter(id=farm)

        plants = Plant.objects.filter(crop__farm__in=farms)
        tx = Transaction.objects.filter(farm__in=farms)
        income = tx.filter(type=Transaction.INCOME).aggregate(t=Sum('amount'))['t'] or 0
        expense = tx.filter(type=Transaction.EXPENSE).aggregate(t=Sum('amount'))['t'] or 0

        return Response({
            'farms': farms.count(),
            'crops': Crop.objects.filter(farm__in=farms).count(),
            'plants': plants.count(),
            'plants_need_care': plants.filter(needs_care=True).count(),
            'open_tasks': Task.objects.filter(farm__in=farms, is_done=False).count(),
            'total_income': str(income),
            'total_expense': str(expense),
            'net': str(income - expense),
        })


class FarmViewSet(viewsets.ModelViewSet):
    """CRUD for farms, scoped to the logged-in user."""
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer

    def get_queryset(self):
        # Only the current user's farms — controls list/retrieve/update/delete.
        return super().get_queryset().filter(owner=self.request.user)

    def perform_create(self, serializer):
        # New farms are automatically owned by whoever created them.
        serializer.save(owner=self.request.user)