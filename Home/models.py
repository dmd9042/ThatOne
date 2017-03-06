from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import AbstractUser, Group
from Dashboard.models import *

Group.objects.get_or_create(name='doctor')
Group.objects.get_or_create(name='nurse')
Group.objects.get_or_create(name='admin')
Group.objects.get_or_create(name='patient')


class User(AbstractUser):
    fName = models.CharField(max_length=30)
    lName = models.CharField(max_length=30)
    street = models.CharField(max_length=50)
    town = models.CharField(max_length=30)
    zipCode = models.IntegerField(null=True)
    birthday = models.DateField(null=True)
    state = models.CharField(max_length=2)
    phone = models.CharField(max_length=10)


class PatientUser(models.Model):
    user = models.OneToOneField(User)
    currHospital = models.ForeignKey(Hospital, null=True, related_name='admittedpatients')
    hospital = models.ForeignKey(Hospital)
    medicalInfo = models.OneToOneField(Medical)

    @classmethod
    def create_patient(cls, user, hospital, medical):
        user.groups.add(Group.objects.get(name='patient'))
        user.save()
        patient = cls(user=user, hospital=hospital, medicalInfo=medical)
        return patient


class DoctorUser(models.Model):
    user = models.OneToOneField(User)
    hospital = models.ForeignKey(Hospital)

    @classmethod
    def create_doctor(cls, user, hospital):
        user.groups.add(Group.objects.get(name='doctor'))
        user.save()
        doctor = cls(user=user, hospital=hospital)
        return doctor


class NurseUser(models.Model):
    user = models.OneToOneField(User)
    doctor = models.ForeignKey(DoctorUser)

    @classmethod
    def create_nurse(cls, user, doctor):
        user.groups.add(Group.objects.get(name='nurse'))
        user.save()
        nurse = cls(user=user, doctor=doctor)
        return nurse


class AdminUser(models.Model):
    user = models.OneToOneField(User)
    hospital = models.OneToOneField(Hospital)

    @classmethod
    def create_admin(cls, user, hospital):
        user.is_staff = True
        user.groups.add(Group.objects.get(name='admin'))
        user.save()
        admin = cls(user=user, hospital=hospital)
        return admin
