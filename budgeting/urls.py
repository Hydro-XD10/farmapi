from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, TransactionViewSet, BudgetSummaryView

# Mounted under /api/ -> /api/categories/, /api/transactions/, /api/budget/summary/
router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('transactions', TransactionViewSet, basename='transaction')

urlpatterns = router.urls + [
    path('budget/summary/', BudgetSummaryView.as_view(), name='budget-summary'),
]
