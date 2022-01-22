from django.db import models

import django
django.setup()


class User(models.Model):
    """Some User Table."""
    class Meta:
        db_table = 'user'
        unique_together = (('level', 'coeff'), )
    id = models.IntegerField('UserId', primary_key=True)
    level = models.IntegerField('User level', default=1)
    nickname = models.CharField('Nickname', unique=True, max_length=20)
    is_active = models.BooleanField(default=True)
    coeff = models.FloatField(default=1.1)
    signature = models.BinaryField(default=b'0101')
    reg_time = models.DateTimeField(auto_now=True)
    birthday = models.DateField(auto_now_add=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)


class Payment(models.Model):
    class Meta:
        db_table = 'payment'
    id = models.IntegerField('PaymentId', primary_key=True)
    sum = models.DecimalField()
    user = models.ForeignKey(User, related_name='user', null=False, on_delete=models.DO_NOTHING,)
