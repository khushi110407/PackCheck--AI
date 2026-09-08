from django.db import models


class ComplianceReport(models.Model):

    product_name = models.CharField(
        max_length=255,
        blank=True
    )

    category = models.CharField(
        max_length=100,
        blank=True
    )

    ocr_text = models.TextField(
        blank=True
    )

    ocr_success = models.BooleanField(
        default=False
    )

    manufacturer = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    net_quantity = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    mrp = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    manufacturing_date = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    consumer_care = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    # AI / ML fields
    ml_label = models.CharField(
        max_length=100,
        blank=True,
        default="UNKNOWN"
    )

    ml_confidence = models.FloatField(
        default=0.0
    )

    detected_keywords = models.JSONField(
        default=list,
        blank=True
    )

    detected_categories = models.JSONField(
        default=list,
        blank=True
    )

    # Compliance
    score = models.PositiveIntegerField(
        default=0
    )

    status = models.CharField(
        max_length=50,
        default="Analysis Pending"
    )

    violation_count = models.PositiveIntegerField(
        default=0
    )

    violations = models.JSONField(
        default=list,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        if self.product_name:
            return f"{self.product_name} - {self.status}"

        return f"Compliance Report #{self.id}"