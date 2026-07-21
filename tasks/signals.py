from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task


@receiver(post_save, sender=Task)
def sync_task_expense(sender, instance,created, **kwargs):
    """Keep budgeting in sync with task costs.

    A task with a cost gets exactly one linked expense Transaction, created or
    updated on every save; clearing the cost removes it. Budgeting stays the single
    source of truth, so /api/budget/summary/ automatically includes task costs.
    Deleting the task cascades the transaction away (OneToOne on_delete=CASCADE).
    """
    from budgeting.models import Transaction   # local import avoids app-load cycles

    if created:
        if instance.cost:
            Transaction.objects.update_or_create(
                task=instance,
                defaults=dict(
                    farm=instance.farm,
                    crop=instance.crop,
                    type=Transaction.EXPENSE,
                    amount=instance.cost,
                    notes=f'مهمة / Task: {instance.title}',
                ),
            )
        else:
            Transaction.objects.filter(task=instance).delete()
