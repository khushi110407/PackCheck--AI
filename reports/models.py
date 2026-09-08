from django.db import models


class ComplianceReport(models.Model):

    # -----------------------------------------
    # Product Information
    # -----------------------------------------

    product_name = models.CharField(
        max_length=255,
        blank=True
    )

    category = models.CharField(
        max_length=100,
        blank=True
    )


    # -----------------------------------------
    # OCR Result
    # -----------------------------------------

    ocr_text = models.TextField(
        blank=True
    )

    ocr_success = models.BooleanField(
        default=False
    )


    # -----------------------------------------
    # Detected Declarations
    # -----------------------------------------

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


    # -----------------------------------------
    # Compliance Result
    # -----------------------------------------

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


    # -----------------------------------------
    # Timestamps
    # -----------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    # -----------------------------------------
    # Display
    # -----------------------------------------

    def __str__(self):

        if self.product_name:
            return (
                f"{self.product_name} - "
                f"{self.status}"
            )

        return (
            f"Compliance Report #{self.id}"
        )