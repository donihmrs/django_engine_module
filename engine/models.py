from django.db import models

class Module(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    author = models.CharField(max_length=50, blank=True, null=True)
    version = models.CharField(max_length=20, default="1.0")
    is_active = models.BooleanField(default=False)
    installed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"