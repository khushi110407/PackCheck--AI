from django.db import models


class ProductScan(models.Model):

    product_name = models.CharField(
        max_length=255,
        blank=True
    )

    category = models.CharField(
        max_length=100,
        blank=True
    )

    product_image = models.ImageField(
        upload_to='products/'
    )

    scanned_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.product_name or f"Scan {self.id}"