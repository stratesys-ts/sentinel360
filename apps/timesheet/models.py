from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import timedelta, datetime

class Activity(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Atividade"
        verbose_name_plural = "Atividades"

    def __str__(self):
        return self.name

class Timesheet(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        SUBMITTED = 'SUBMITTED', _('Submitted')
        PARTIALLY_APPROVED = 'PARTIALLY_APPROVED', _('Partially Approved')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='timesheets')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_timesheets')
    partial_approvers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='partially_approved_timesheets')
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        unique_together = ['user', 'start_date']

    def __str__(self):
        return f"{self.user} ({self.start_date} - {self.end_date})"

class TimeEntry(models.Model):
    timesheet = models.ForeignKey(Timesheet, on_delete=models.CASCADE, related_name='entries', null=True, blank=True)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='time_entries', null=True, blank=True)
    task = models.ForeignKey('projects.Task', on_delete=models.SET_NULL, null=True, blank=True, related_name='time_entries')
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True, blank=True)
    
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    description = models.TextField(blank=True)
    
    # Legacy fields (kept for compatibility or detailed view if needed, but 'hours' is primary for grid)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'project']
        verbose_name = "Lançamento de horas"
        verbose_name_plural = "Lançamentos de horas"

    def __str__(self):
        return f"{self.date} - {self.project} - {self.hours}h"
