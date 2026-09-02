from rest_framework import viewsets
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Sum
from decimal import Decimal
from .models import Category, Transaction
from .serializers import CategorySerializer, TransactionSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD for categories.

    Reads return the user's own-farm categories PLUS shared system categories
    (farm=NULL). Writes are restricted to the user's own categories, so nobody can
    edit or delete a shared system category through the API.
    Optional ?farm=<id> filter.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if self.request.method in SAFE_METHODS:
            # GET: my categories + global/system ones.
            qs = qs.filter(Q(farm__owner=user) | Q(farm__isnull=True))
        else:
            # PUT/PATCH/DELETE: only my own — system categories are protected.
            qs = qs.filter(farm__owner=user)
        farm = self.request.query_params.get('farm')
        if farm:
            qs = qs.filter(farm_id=farm)
        return qs


class BudgetSummaryView(APIView):
    """GET /api/budget/summary/ -> total income, total expenses, and net for the
    logged-in user. Optional ?farm=<id> to limit to one farm.

    Task costs are included automatically because each costed task has a linked
    expense Transaction (tasks/signals.py) — totals come from one source of truth.
    """
    def get(self, request):
        qs = Transaction.objects.filter(farm__owner=request.user)
        farm = request.query_params.get('farm')
        if farm:
            qs = qs.filter(farm_id=farm)
        income = qs.filter(type=Transaction.INCOME).aggregate(t=Sum('amount'))['t'] or 0
        expense = qs.filter(type=Transaction.EXPENSE).aggregate(t=Sum('amount'))['t'] or 0

        # Per-category and per-crop breakdowns. Sum(filter=...) puts income and
        # expense side by side in one grouped query; NULL group = uncategorized /
        # not tied to a crop.
        def breakdown(label_field, label_key):
            rows = (qs.values(label_field)
                      .annotate(income=Sum('amount', filter=Q(type=Transaction.INCOME)),
                                expense=Sum('amount', filter=Q(type=Transaction.EXPENSE)))
                      .order_by(label_field))
            out = []
            for r in rows:
                inc = r['income'] or Decimal('0')
                exp = r['expense'] or Decimal('0')
                out.append({label_key: r[label_field], 'income': str(inc),
                            'expense': str(exp), 'net': str(inc - exp)})
            return out

        # Money as strings, matching how DRF serializes DecimalFields elsewhere
        # (e.g. "150.50") — avoids float precision issues in clients.
        return Response({
            'total_income': str(income),
            'total_expense': str(expense),
            'net': str(income - expense),
            'by_category': breakdown('category__name', 'category'),
            'by_crop': breakdown('crop__name', 'crop'),
        })


class TransactionViewSet(viewsets.ModelViewSet):
    """CRUD for transactions, scoped to the user via the farm's owner.
    Optional filters: ?farm=<id>, ?crop=<id>, ?type=income|expense."""
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(farm__owner=self.request.user)
        farm = self.request.query_params.get('farm')
        crop = self.request.query_params.get('crop')
        type_ = self.request.query_params.get('type')
        if farm:
            qs = qs.filter(farm_id=farm)
        if crop:
            qs = qs.filter(crop_id=crop)
        if type_:
            qs = qs.filter(type=type_)
        return qs
