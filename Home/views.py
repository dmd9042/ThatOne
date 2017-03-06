from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.template.defaulttags import csrf_token
from .forms import *
from .models import *
from django.contrib.auth import *
from django.contrib import messages
from datetime import datetime
import logging
from django.db import IntegrityError
from django.utils import timezone

def home(request):
    """
    This will display the home page for HealthNet, when your first connect to the server this will serve the
    first page the user will see
    :param request: HTTP request given from the web browser
    :return: A new rendered html template
    """
    context = {}
    if 'lsucess' in request.GET:
        context['message'] = "User created successfully"
    elif 'errorn' in request.GET:
        context['error'] = "Username/Password Incorrect"
    return render(request, 'Home/home.html', context)


def signUp(request):
    """
    This will display the sign up page with all of the input fields
    :param request: HTTP request given from the web browser
    :return: This will return the user to the home page with the new user created allowing them to log in
    """
    if request.method == 'POST':
        try:
            user = User.objects.create_user(request.POST.get("usr"), request.POST.get("email"), request.POST.get("password"))
        except IntegrityError as e:
            return HttpResponseRedirect('/home/signUp/?fusern')
        user.fName = request.POST.get("fName")
        user.lName = request.POST.get("lName")
        user.street = request.POST.get("street")
        user.town = request.POST.get("town")
        user.state = request.POST.get("state")
        user.zipCode = request.POST.get("zip")
        user.phone = request.POST.get("phone")

        user.birthday = request.POST.get("birthDay")
        med = Medical.create_medical(tests=Test.objects.create(), prescriptions=Prescription.objects.create())
        med.save()
        patient = PatientUser.create_patient(user=user, hospital=Hospital.objects.get(name=request.POST.get("hospital")), medical=med)

        user.save()
        patient.save()
        # Logging
        dataLogger = logging.getLogger("dataLogger")
        dataLogger.info(user.get_username() + " newuser " + datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M") +
                        " " + patient.hospital.name)
        # End logging
        return HttpResponseRedirect('/home/?lsucess')
    else:
        hos = Hospital.objects.all()
        context = {}
        if 'fusern' in request.GET:
            context['message'] = "User Name already taken"
        context['hospitals'] = hos
        return render(request,'Home/signUp.html',context)


def logIn(request):
    """
    This will handle the user logging into the system from the home page, and redirect to the appropriate dashboard
    :param request: HTTP request given from the web browser
    :return: This will return the logged in user either to a new log in screen or their dashboard
    """

    if request.method == 'POST':
        user = authenticate(username=request.POST.get("usr"), password=request.POST.get("password"))

        if user is not None:
            login(request, user)
            request.session[user.id] = user.username
            path = '/dash/' + str(user.pk) + '/'
            return HttpResponseRedirect(path)
        else:
            return HttpResponseRedirect('/home/?errorn')
    else:
        context = {}
        if 'login' in request.GET:
            context['message'] = "You do not have permission to do that"
        elif 'fail' in request.GET:
            context['message'] = "Incorrect username or password"
        return render(request, 'Home/logIn.html', context)

def logOut(request):
    if request.method=='POST':
        logout(request)
        return HttpResponseRedirect('/home/')
    else:
        return HttpResponseRedirect('/home/')


def help(request):
    """
    This will display the help page that is linked in the header, this contains information for use of the system/
    contact information and other important information for the system.
    :param request: HTTP request given from the web browser
    :return: This will return the user to the help page
    """
    return render(request, 'Home/help.html')