from django.db import models


class Member(models.Model):
    member_id = models.CharField(max_length=50, unique=True)
    id_type = models.CharField(max_length=50)
    name = models.CharField(max_length=70)
    registered_on = models.DateTimeField(auto_now_add=True)
    constituency = models.CharField(max_length=50)

    class Meta:
        unique_together = ('member_id', 'id_type', )

    def __str__(self):
        return self.name


class Payment(models.Model):
    amount = models.DecimalField(default=1.0, decimal_places=2, max_digits=10)
    initiated_on = models.DateTimeField(auto_now_add=True)
    confirmed_on = models.DateTimeField(null=True)
    member = models.CharField(max_length=70)
    constituency = models.CharField(max_length=50)
