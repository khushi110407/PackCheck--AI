from django.db import models


class ComplianceCheck(models.Model):

    STATUS_CHOICES = [
        ('COMPLIANT', 'Compliant'),
        ('NON_COMPLIANT', 'Non-Compliant'),
        ('PENDING', 'Pending'),
    ]

    product_name = models.CharField(
        max_length=255
    )

    product_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    compliance_score = models.FloatField(
        default=0
    )

    violations_count = models.PositiveIntegerField(
        default=0
    )

    checked_at = models.DateTimeField(
        auto_now_add=True
    )

    remarks = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.product_name