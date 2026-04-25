from django.db import models

class VerificationCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)

    def __str__(self):
        return self.email