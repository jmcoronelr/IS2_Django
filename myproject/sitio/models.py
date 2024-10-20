from django.db import models

class SiteSettings(models.Model):
    maintenance_mode = models.BooleanField(default=False)

