from django.db import models
from datetime import date

class Hospital(models.Model):
    name = models.CharField(max_length=100, default="Hospital", null=True)
    capacity = models.IntegerField(default=100)
    currentPatients = models.IntegerField(default=0)


class Test(models.Model):
    name = models.CharField(max_length=100, default="Name")
    result = models.CharField(max_length=100, default="Result")
    release = models.BooleanField(default=False)


class Prescription(models.Model):
    name = models.CharField(max_length=100, default="Name")
    dosage = models.CharField(max_length=7, default="Dosage")
    given = models.DateField(default=date.today)
    expire = models.DateField(default=date.today)


class Medical(models.Model):
    tests = models.ForeignKey(Test)
    prescriptions = models.ForeignKey(Prescription)

    @classmethod
    def create_medical(cls, tests, prescriptions):
        medical = cls(tests=tests, prescriptions=prescriptions)
        return medical
