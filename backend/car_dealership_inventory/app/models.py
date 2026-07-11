from django.db import models

# Create your models here.
class vehicles(models.Model):
    id=models.AutoField(primary_key=True)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    quantity = models.IntegerField()
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    

    def __str__(self):
        return self.make