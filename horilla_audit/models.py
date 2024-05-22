"""
models.py
"""

from collections.abc import Iterable
from django.db import models
from django.dispatch import receiver
from simple_history.models import (
    HistoricalRecords,
    _default_get_user,
    _history_user_getter,
    _history_user_setter,
)
from simple_history.signals import (
    post_create_historical_record,
    pre_create_historical_record,
    # pre_create_historical_m2m_records,
    # post_create_historical_m2m_records,
)

# from employee.models import Employee
from Mibs.models import MibsModel
from Mibs_audit.methods import remove_duplicate_history


# Create your models here.


class AuditTag(models.Model):
    """
    HistoryTag model
    """

    title = models.CharField(max_length=20)
    highlight = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.title)

    class Meta:
        """
        Meta class for aditional info
        """

        app_label = "Mibs_audit"


class MibsAuditInfo(models.Model):
    """
    MibsAuditInfo model to store additional info
    """

    history_title = models.CharField(max_length=20, null=True, blank=True)
    history_description = models.TextField(null=True)
    history_highlight = models.BooleanField(default=False, null=True)
    history_tags = models.ManyToManyField(AuditTag)

    class Meta:
        """
        Meta class for aditional info
        """

        app_label = "Mibs_audit"
        abstract = True


class MibsAuditLog(HistoricalRecords):
    """
    Model to store additional information for historical records.
    """

    # def __init__(self, *args, bases=None, **kwargs):
    #     super(MibsAuditLog, self).__init__(*args, **kwargs)
    #     self.is_Mibs_audit_log = True

    pass

    # history_comments = models.ManyToManyField("HistoryComment", blank=True)


@receiver(pre_create_historical_record)
def pre_create_Mibs_audit_log(sender, instance, *args, **kwargs):
    """
    Pre create horill audit log method
    """
    try:
        history_instance = kwargs["history_instance"]
        history_instance.history_title = HistoricalRecords.thread.request.POST.get(
            "history_title"
        )
        history_instance.history_description = (
            HistoricalRecords.thread.request.POST.get("history_description")
        )
        history_instance.history_highlight = (
            True
            if HistoricalRecords.thread.request.POST.get("history_highlight") == "on"
            else False
        )
        instance.skip_history = True
    except:
        pass


@receiver(post_create_historical_record)
def post_create_Mibs_audit_log(sender, instance, *_args, **kwargs):
    """
    Post create horill audit log method
    """
    try:
        history_instance = kwargs["history_instance"]
        history_instance.history_tags.set(
            HistoricalRecords.thread.request.POST.getlist("history_tags")
        )
        if isinstance(history_instance, MibsAuditLog):
            history_instance.history_title = "Demo Title"
            remove_duplicate_history(instance)
            if instance.skip_history:
                instance.history_set.filter(pk=history_instance.pk).delete()
            kwargs["history_instance"] = None
    except:
        pass


class HistoryTrackingFields(MibsModel):
    tracking_fields = models.JSONField(null=True, blank=True, editable=False)


class AccountBlockUnblock(MibsModel):
    is_enabled = models.BooleanField(default=False, null=True, blank=True)
