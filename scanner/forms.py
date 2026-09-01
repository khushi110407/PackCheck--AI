from django import forms
from .models import ProductScan


class ProductScanForm(forms.ModelForm):

    class Meta:
        model = ProductScan

        fields = [
            'product_name',
            'category',
            'product_image',
        ]

        labels = {
            'product_name': 'Product Name',
            'category': 'Product Category',
            'product_image': 'Upload Product Image',
        }

        widgets = {
            'product_name': forms.TextInput(
                attrs={
                    'placeholder': 'Enter product name',
                    'class': 'form-control',
                }
            ),

            'category': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. Food, Cosmetics, Electronics',
                    'class': 'form-control',
                }
            ),

            'product_image': forms.ClearableFileInput(
                attrs={
                    'accept': 'image/*',
                    'class': 'form-control',
                }
            ),
        }