import uuid
from django.db import models


class Category(models.Model):
    """فئة — a budgeting category for income/expense grouping.

    Two kinds (see [[farmapi-bilingual]] for the naming decision still pending):
      • System/default: farm = NULL, is_user_made = False — shared by everyone.
      • User-made:      farm = <a farm>, is_user_made = True — private to that farm.
    name is free text (English or Arabic).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # NULL farm marks a global/system category; SET on user-made ones.
    farm = models.ForeignKey('farm.Farm', on_delete=models.CASCADE,
                             null=True, blank=True, related_name='categories')
    name = models.CharField(max_length=255)
    is_user_made = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """معاملة — a single income or expense entry for a farm."""
    INCOME = 'income'
    EXPENSE = 'expense'
    TYPE_CHOICES = [(INCOME, 'Income'), (EXPENSE, 'Expense')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey('farm.Farm', on_delete=models.CASCADE, related_name='transactions')
    # Deleting a crop/category shouldn't erase financial history — just detach it.
    crop = models.ForeignKey('crops.Crop', on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='transactions')
    # Set only by the server: links the auto-created expense for a Task's cost
    # (see tasks/signals.py). Deleting the task removes its expense too.
    task = models.OneToOneField('tasks.Task', on_delete=models.CASCADE,null=True, blank=True, related_name='expense_transaction')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    # DecimalField (not float) so money never suffers rounding errors.
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date_gregorian = models.DateField(null=True, blank=True)   # التاريخ الميلادي
    date_hijri = models.CharField(max_length=20, blank=True, null=True)  # التاريخ الهجري (text)
    from_supplier = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            # Django 6.0 uses `condition=` (was `check=` in older versions).
            models.CheckConstraint(condition=models.Q(type__in=['income', 'expense']),
                                   name='transaction_type_valid'),
        ]

    def __str__(self):
        return f'{self.type} {self.amount}'
