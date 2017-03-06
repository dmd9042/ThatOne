from django.db import models

from Home.models import PatientUser, DoctorUser
from Dashboard.models import Hospital

# Create your models here.
class Appointment(models.Model):
    title = models.CharField(max_length=64)
    start = models.DateTimeField()
    end = models.DateTimeField()
    patient = models.ForeignKey(PatientUser)
    doctor = models.ForeignKey(DoctorUser)
    hospital = models.ForeignKey(Hospital)