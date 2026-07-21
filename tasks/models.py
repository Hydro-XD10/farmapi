import uuid
from django.db import models


class TaskCategory(models.Model):
    """فئة مهام — user-made task category (e.g. ري، تقليم). No rigid predefined
    ones; every category belongs to a farm and is created by its owner."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey('farm.Farm', on_delete=models.CASCADE,
                             related_name='task_categories')
    name = models.CharField(max_length=255)   # EN/AR

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Task categories'

    def __str__(self):
        return self.name


class Task(models.Model):
    """مهمة — a to-do item for a farm, optionally tied to a specific crop.

    title is free text in English or Arabic (bilingual app). priority is a fixed
    set of choices; the label values ('Low'...) are display fallbacks that the app
    localizes.
    """
    LOW, MEDIUM, HIGH = 'low', 'medium', 'high'
    PRIORITY_CHOICES = [(LOW, 'Low'), (MEDIUM, 'Medium'), (HIGH, 'High')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # CASCADE: a task can't outlive its farm. SET_NULL on crop so deleting a crop
    # detaches the task instead of erasing task history.
    farm = models.ForeignKey('farm.Farm', on_delete=models.CASCADE, related_name='tasks')
    crop = models.ForeignKey('crops.Crop', on_delete=models.SET_NULL,null=True, blank=True, related_name='tasks')
    # Plant lives in the crops app -> 'crops.Plant'. Its own related_name so it
    # doesn't clash with crop's 'tasks' reverse accessor (access via plant.plant_tasks).
    plant = models.ForeignKey('crops.Plant', on_delete=models.SET_NULL,
                              null=True, blank=True, related_name='plant_tasks')
    title = models.CharField(max_length=255)
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, null=True, blank=True)
    is_done = models.BooleanField(default=False)
    # cost auto-syncs to an expense Transaction in budgeting (see tasks/signals.py),
    # so it is counted in total expenses without double bookkeeping.
    cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    hours_spent = models.FloatField(null=True, blank=True)
    assigned_to = models.CharField(max_length=255, null=True, blank=True)  # اسم العامل / who works on it
    category = models.ForeignKey(TaskCategory, on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
