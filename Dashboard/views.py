from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from Home.models import *
from Dashboard.forms import *
from Dashboard.models import *
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from Calenda.models import Appointment
from django.db.models import F
from django.utils import timezone
import logging
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

def tab(id, name, url, template):
    return {
        'id': id,
        'name': name,
        'url': url,
        'template': template
    }


tabCalendar = tab('calendar', 'Calendar', 'calendar/', 'Calenda/calendar.html')
tabAppCreate = tab('appcreate', 'Create Appointment', 'Appointment/new/', 'Calenda/appcreate.html')
tabAppUpdate = tab('appupdate', 'Update Appointment', 'Appointment/#/', 'Calenda/appupdate.html')
tabAdmit = tab('admit', 'Admit', 'admit/', 'Dashboard/admit.html')
tabTransfer = tab('transfer', 'Transfer', 'transfer/', 'Dashboard/transfer.html')
tabDischarge = tab('discharge', 'Discharge', 'discharge/', 'Dashboard/discharge.html')
tabTests = tab('tests', 'Tests', 'tests/', 'Dashboard/tests.html')
tabCreate = tab('create', 'Create Entity', 'create/', 'Dashboard/create.html')
tabProfile = tab('profile', 'Profile', '', 'Dashboard/edit.html')
tabLog = tab('log', 'Log', 'log/', 'Dashboard/log.html')
tabMessage = tab('message', 'Messaging', 'message/', 'Dashboard/message.html')


def getTabs(user_id):
    user = User.objects.get(pk=user_id)

    if user.groups.filter(name='doctor').exists():
        return [tabProfile, tabCalendar, tabAdmit, tabTransfer, tabDischarge]
    elif user.groups.filter(name='nurse').exists():
        return [tabProfile, tabCalendar, tabAdmit]
    elif user.groups.filter(name='admin').exists():
        return [tabProfile, tabTransfer, tabCreate, tabLog]
    else:
        return [tabProfile, tabCalendar]

"""
@login_required()
def message(request, user_id):
    user = User.objects.get(pk=user_id)
    if request.method == 'POST':
        toUser = request.POST['to']
        fromUser = user
        text = request.POST['text']
        timestamp = timezone.now()

        user.save()
        return HttpResponseRedirect("/dash/" + str(user.id) + "/message/")
    else:
        context = {
            'user': user,
            'tabs': getTabs(user_id),
            'messages': Message.objects.filter(fromUser=user) | Message.objects.filter(toUser=user)
            'users': User.object.all(),
            'tab': tabMessage
        }
        return render(request, 'Dashboard/dash.html', context)"""


@login_required()
def dashboard(request, user_id):
    """
    This will display the specific dashboard for the user that is currently signed into the system
    :param request: HTTP request from the browser
    :return: Return a loaded template of the specific dashboard with their specific info loaded in
    """

    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        user.fName = request.POST.get("fName")
        user.lName = request.POST.get("lName")
        user.birthday = datetime.strptime(request.POST.get("birthDay"), '%Y-%m-%d')
        user.email = request.POST.get("email")
        user.phone = request.POST.get("phone")
        user.save()
        # Logging
        dataLogger = logging.getLogger("dataLogger")
        hospitalName = ""
        try:
            hospitalName = user.hospital.name
        except AttributeError:
            hospitalName = "N/A"
        dataLogger.info(user.get_username() + " dashboardUpdate " + datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M") +
                        " " + hospitalName)
        # End logging
        return HttpResponseRedirect("/dash/" + str(user.id) + "/")
    else:
        context = {
            'userr': user,
            "tabs": getTabs(user_id),
            "tab": tabProfile
        }
        return render(request, 'Dashboard/dash.html', context)


def isAdmin(user):
    if user.groups.filter(name='admin').exists():
        return True
    return False


def getLog(start, end, user, eventType, hospital):
    """
    Return a plaintext string that contains the log events filtered based on the arguments
    :param start: datetime object, start of timeframe to display events from
    :param end: datetime object, end of timeframe to display events from
    :param user: User object, filter events to those which this user is related to. May be null
    :param eventType: string, filter to events of this type. May be null
    :param hospital: Hospital object, filter events to those which this hospital is related to. May be null
    :return: plaintext string
    """
    logString = ""

    with open("HealthNet.log") as f:
        lines = f.readlines()
    processed_lines = []
    for line in lines:
        split_line = line.split()
        time = timezonify_str(split_line[2] + " " + split_line[3])
        if (((user is None) or (user.username == split_line[0])) and
                ((eventType is None) or eventType == split_line[1]) and
                ((hospital is None) or hospital.name == split_line[4]) and
                ((start is None) or (time >= start)) and
                ((end is None) or (time <= end))):
            processed_lines.append(split_line)
    for chosen_one in processed_lines:
        for one in chosen_one:
            logString += one
            logString += " "
        logString += "\n"
    return logString


@user_passes_test(isAdmin)
def log(request, user_id):
    user = User.objects.get(pk=user_id)

    if request.method == 'GET':
        context = {
            "userr": user,
            "users": User.objects.all(),
            "hospitals": Hospital.objects.all(),
            "tab": tabLog,
            "tabs": getTabs(user_id)
        }
        return render(request, 'Dashboard/dash.html', context)
    else:
        start = timezonify_str(request.POST["start"])
        end = timezonify_str(request.POST["end"])
        user = None
        eventType = None
        hospital = None

        if request.POST["user"] != '':
            user = User.objects.get(username=request.POST["user"])
        if request.POST["type"] != '':
            eventType = request.POST["type"]
        if request.POST["hospital"] != '':
            hospital = Hospital.objects.get(name=request.POST["hospital"])

        text = getLog(start, end, user, eventType, hospital)
        return HttpResponse(text, content_type="text/plain")


"""if user.groups.filter(name='doctor').exists():
    tabs = [tabCalendar, tabAdmit, tabTransfer, tabDischarge]
    context = {"user": user, "tabs": tabs, "tab": tabs[0]}
    return render(request, 'Dashboard/dash.html', context)
elif user.groups.filter(name='nurse').exists():
    tabs = [tabCalendar, tabAdmit]
    context = {"user": user, "tabs": tabs, "tab": tabs[0]}
    return render(request, 'Dashboard/dash.html', context)
elif user.groups.filter(name='admin').exists():
    tabs = [tabTransfer]
    context = {"user": user, "tabs": tabs, "tab": tabs[0]}
    return render(request, 'Dashboard/dash.html', context)
else:
    tabs = [tabCalendar]
    context = {"user": user, "tabs": tabs, "tab": tabs[0]}
    return render(request, 'Dashboard/dash.html', context)"""


def medInfo(request, user_id, patient_id=-1):
    if patient_id == -1:
        patient_id = user_id


def basic(request, user_id):
    user = User.objects.get(pk=user_id)
    patient = PatientUser.objects.get(user=user)
    day = datetime.strftime(user.birthday, '%Y-%m-%d')
    return render(request, 'Dashboard/basic.html', context={"patient": patient, "birth": day})


def tests(request, user_id):
    """user = User.objects.get(pk=user_id)
    patient = PatientUser.objects.get(user=user)
    day = datetime.strftime(user.birthday, '%Y-%m-%d')
    return render(request, 'Dashboard/tests.html', context={"patient": patient, "birth": day})"""
    user = User.objects.get(pk=user_id)



def pres(request, user_id):
    user = User.objects.get(pk=user_id)
    patient = PatientUser.objects.get(user=user)
    day = datetime.strftime(user.birthday, '%Y-%m-%d')
    return render(request, 'Dashboard/prescriptions.html', context={"patient": patient, "birth": day})


def hospital(request, user_id):
    user = User.objects.get(pk=user_id)
    patient = PatientUser.objects.get(user=user)
    day = datetime.strftime(user.birthday, '%Y-%m-%d')
    return render(request, 'Dashboard/admissions.html', context={"patient": patient, "birth": day})


def messages(request, user_id):
    user = User.objects.get(pk=user_id)
    patient = PatientUser.objects.get(user=user)
    day = datetime.strftime(user.birthday, '%Y-%m-%d')
    return render(request, 'Dashboard/dashboard.html', context={"patient": patient, "birth": day})


@login_required()
def calendar(request, user_id):
    # user = User.objects.get(pk=user_id)
    # patient = PatientUser.objects.get(user=user)
    # day = datetime.strftime(user.birthday, '%Y-%m-%d')

    user = User.objects.get(pk=user_id)

    if user.groups.filter(name='doctor').exists():
        appointments = Appointment.objects.filter(doctor__user__id=user_id)
    elif user.groups.filter(name='patient').exists():
        appointments = Appointment.objects.filter(patient__user__id=user_id)
    elif user.groups.filter(name='nurse').exists():
        appointments = Appointment.objects.filter(doctor=NurseUser.objects.get(user__id=user_id).doctor)
    else:
        appointments = []

    context = {
        "appointments": appointments,
        "tabs": getTabs(user_id),
        "tab": tabCalendar,
        "userr": user
        # "patient": patient,
        # "birth": day
    }
    return render(request, 'Dashboard/dash.html', context)


def isDoctorAdmin(user):
    if user.groups.filter(name='doctor').exists() or user.groups.filter(name='admin').exists():
        return True
    return False


@user_passes_test(isDoctorAdmin)
def transfer(request, user_id):
    user = User.objects.get(pk=user_id)
    if user.groups.filter(name='doctor').exists():
        return transferDoctor(request, user_id)
    elif user.groups.filter(name='admin').exists():
        return transferAdmin(request, user_id)


def transferDoctor(request, user_id):
    user = User.objects.get(pk=user_id)
    doctor = DoctorUser.objects.get(user=user)
    patients = PatientUser.objects.filter(currHospital__isnull=False)
    hospitals = [doctor.hospital]

    if request.method == 'GET':
        context = transferGeneric(request, user_id)
        context["patients"] = patients
        context["doctor"] = doctor
        context["hospitals"] = hospitals
        return render(request, 'Dashboard/dash.html', context)
    else:
        transferGeneric(request, user_id)
        return HttpResponseRedirect("/dash/" + str(user.id) + "/transfer/")


def transferAdmin(request, user_id):
    user = User.objects.get(pk=user_id)
    admin = AdminUser.objects.get(user=user)
    patients = PatientUser.objects.filter(currHospital__isnull=False)
    hospitals = Hospital.objects.all()

    if request.method == 'GET':
        context = transferGeneric(request, user_id)
        context["patients"] = patients
        context["admin"] = admin
        context["hospitals"] = hospitals
        return render(request, 'Dashboard/dash.html', context)
    else:
        transferGeneric(request, user_id)
        return HttpResponseRedirect("/dash/" + str(user.id) + "/transfer/")


def transferGeneric(request, user_id):
    user = User.objects.get(pk=user_id)
    if request.method == 'GET':
        context = {
            "userr": user,
            "tab": tabTransfer,
            "tabs": getTabs(user_id)
        }
        return context
    else:
        patient = PatientUser.objects.get(user__username=request.POST["patient"])
        hospital = Hospital.objects.get(name=request.POST["hospital"])
        patient.currHospital.currentPatients -= 1
        patient.currHospital.save()
        patient.currHospital = hospital
        hospital.currentPatients += 1
        hospital.save()
        patient.save()
        # Logging
        dataLogger = logging.getLogger("dataLogger")
        dataLogger.info(user.get_username() + " transfer " + datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M") +
                        " " + patient.hospital.name + " patient: " + patient.user.username)
        # End logging


def isDoctor(user):
    if user.groups.filter(name='doctor').exists():
        return True
    return False


@user_passes_test(isDoctor)
def discharge(request, user_id):
    user = User.objects.get(pk=user_id)
    doctor = DoctorUser.objects.get(user=user)
    patients = PatientUser.objects.filter(hospital__in=[doctor.hospital]).filter(currHospital__isnull=False)

    if request.method == 'GET':
        context = {
            "userr": user,
            "patients": patients,
            "doctor": doctor,
            "tab": tabDischarge,
            "tabs": getTabs(user_id)
        }
        return render(request, 'Dashboard/dash.html', context)
    else:
        patient = PatientUser.objects.get(user__username=request.POST["patient"])
        hospital = patient.currHospital
        patient.currHospital = None
        hospital.currentPatients -= 1
        hospital.save()
        patient.save()
        # Logging
        dataLogger = logging.getLogger("dataLogger")
        dataLogger.info(user.get_username() + " discharge " + datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M") +
                        " " + patient.hospital.name + " patient: " + patient.user.username)
        # End logging
        return HttpResponseRedirect("/dash/" + str(user.id) + "/discharge/")


def isDoctorNurse(user):
    if user.groups.filter(name='doctor').exists() or user.groups.filter(name='nurse').exists():
        return True
    return False


@user_passes_test(isDoctorNurse)
def admit(request, user_id):
    user = User.objects.get(pk=user_id)
    if user.groups.filter(name='doctor').exists():
        return admitDoctor(request, user_id)
    elif user.groups.filter(name='nurse').exists():
        return admitNurse(request, user_id)


def admitDoctor(request, user_id):
    user = User.objects.get(pk=user_id)
    doctor = DoctorUser.objects.get(user=user)
    patients = PatientUser.objects.filter(hospital__in=[doctor.hospital]).filter(currHospital__isnull=True)

    hospitals = [doctor.hospital]

    if request.method == 'GET':
        context = admitGeneric(request, user_id)
        context["patients"] = patients
        context["doctor"] = doctor
        context["hospitals"] = hospitals
        return render(request, 'Dashboard/dash.html', context)
    else:
        admitGeneric(request, user_id)
        return HttpResponseRedirect("/dash/" + str(user.id) + "/admit/")


def admitNurse(request, user_id):
    user = User.objects.get(pk=user_id)
    nurse = NurseUser.objects.get(user=user)
    doctor = nurse.doctor
    patients = PatientUser.objects.filter(hospital__in=[doctor.hospital]).filter(currHospital__isnull=True)

    hospitals = [doctor.hospital]

    if request.method == 'GET':
        context = admitGeneric(request, user_id)
        context["patients"] = patients
        context["doctor"] = doctor
        context["nurse"] = nurse
        context["hospitals"] = hospitals
        return render(request, 'Dashboard/dash.html', context)
    else:
        admitGeneric(request, user_id)
        return HttpResponseRedirect("/dash/" + str(user.id) + "/admit/")


def admitGeneric(request, user_id):
    user = User.objects.get(pk=user_id)
    if request.method == 'GET':
        context = {
            "userr": user,
            "tab": tabAdmit,
            "tabs": getTabs(user_id)
        }
        return context
    else:
        patient = PatientUser.objects.get(user__username=request.POST["patient"])
        hospital = Hospital.objects.get(name=request.POST["hospital"])
        patient.currHospital = hospital
        hospital.currentPatients += 1
        hospital.save()
        patient.save()
        # Logging
        dataLogger = logging.getLogger("dataLogger")
        dataLogger.info(user.get_username() + " admit " + datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M") +
                        " " + patient.hospital.name + " patient: " + patient.user.username)
        # End logging


def isDoctorPatient(user):
    if user.groups.filter(name='doctor').exists() or user.groups.filter(name='patient').exists():
        return True
    return False


@user_passes_test(isDoctorPatient)
def appCreate(request, user_id):
    user = User.objects.get(pk=user_id)
    if user.groups.filter(name='doctor').exists():
        return appCreateDoctor(request, user_id)
    elif user.groups.filter(name='patient').exists():
        return appCreatePatient(request, user_id)
    else:
        pass


def appCreatePatient(request, user_id):
    user = User.objects.get(pk=user_id)
    patient = PatientUser.objects.get(user=user)
    day = datetime.strftime(user.birthday, '%Y-%m-%d')

    if request.method == 'GET':
        context = appCreateGeneric(request, user_id)
        context["patient"] = patient
        context["birth"] = day
        return render(request, 'Dashboard/dash.html', context)
    else:
        appCreateGeneric(request, user_id)
        return HttpResponseRedirect("/dash/" + str(user.id) + "/calendar/")


def appCreateDoctor(request, user_id):
    user = User.objects.get(pk=user_id)
    doctor = DoctorUser.objects.get(user=user)

    if request.method == 'GET':
        context = appCreateGeneric(request, user_id)
        context["doctor"] = doctor
        return render(request, 'Dashboard/dash.html', context)
    else:
        appCreateGeneric(request, user_id)
        return HttpResponseRedirect("/dash/" + str(user.id) + "/calendar/")


def appCreateGeneric(request, user_id):
    user = User.objects.get(pk=user_id)
    if request.method == 'GET':
        if 'start' in request.GET:
            start = request.GET['start']
            end = (datetime.strptime(start, "%Y/%m/%d %H:%M") + timedelta(minutes=30)).strftime("%Y/%m/%d %H:%M")
        else:
            start = ''
            end = ''


        hospitals = Hospital.objects.all()
        doctors = DoctorUser.objects.all()
        patients = PatientUser.objects.all()

        context = {
            "userr": user,
            "starttime": start,
            "endtime": end,
            "hospitals": hospitals,
            "doctors": doctors,
            "patients": patients,
            "tab": tabAppCreate,
            "tabs": getTabs(user_id)
        }
        return context
    else:
        app = Appointment()
        app.title = request.POST["reason"]
        app.start = timezonify_str(request.POST["starttime"])
        app.end = timezonify_str(request.POST["endtime"])
        app.patient = PatientUser.objects.get(user__username=request.POST["patient"])
        app.doctor = DoctorUser.objects.get(user__username=request.POST["doctor"])
        app.hospital = Hospital.objects.get(name=request.POST["hospital"])
        app.save()
        # Logging
        dataLogger = logging.getLogger("dataLogger")
        dataLogger.info(user.get_username() + " createAppt " + datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M") +
                        " " + app.patient.hospital.name + " patient: " + app.patient.user.username)
        # End logging


@login_required()
def appUpdate(request, user_id, app_id):
    user = User.objects.get(pk=user_id)
    if user.groups.filter(name='doctor').exists():
        return appUpdateDoctor(request, user_id, app_id)
    elif user.groups.filter(name='patient').exists():
        return appUpdatePatient(request, user_id, app_id)
    elif user.groups.filter(name='nurse').exists():
        return appUpdateNurse(request, user_id, app_id)
    else:
        pass


def appUpdatePatient(request, user_id, app_id):
    user = User.objects.get(pk=user_id)
    patient = PatientUser.objects.get(user=user)
    day = datetime.strftime(user.birthday, '%Y-%m-%d')

    if request.method == 'GET':
        context = appUpdateGeneric(request, user_id, app_id)
        context["patient"] = patient
        context["birth"] = day
        return render(request, 'Dashboard/dash.html', context)
    else:
        appUpdateGeneric(request, user_id, app_id)
        return HttpResponseRedirect("/dash/" + str(user.id) + "/calendar/")


def appUpdateDoctor(request, user_id, app_id):
    user = User.objects.get(pk=user_id)
    doctor = DoctorUser.objects.get(user=user)
    patients = PatientUser.objects.filter(hospital__in=F('hospital'))

    if request.method == 'GET':
        context = appUpdateGeneric(request, user_id, app_id)
        context["doctor"] = doctor
        context["patients"] = patients
        return render(request, 'Dashboard/dash.html', context)
    else:
        appUpdateGeneric(request, user_id, app_id)
        return HttpResponseRedirect("/dash/" + str(user.id) + "/calendar/")


def appUpdateNurse(request, user_id, app_id):
    user = User.objects.get(pk=user_id)
    doctor = NurseUser.objects.get(user=user).doctor
    patients = PatientUser.objects.filter(hospital__in=F('hospital'))

    if request.method == 'GET':
        context = appUpdateGeneric(request, user_id, app_id)
        context["doctor"] = doctor
        context["patients"] = patients
        return render(request, 'Dashboard/dash.html', context)
    else:
        appUpdateGeneric(request, user_id, app_id)
        return HttpResponseRedirect("/dash/" + str(user.id) + "/calendar/")


def appUpdateGeneric(request, user_id, app_id):
    user = User.objects.get(pk=user_id)
    app = Appointment.objects.get(pk=app_id)

    if request.method == 'GET':
        hospitals = Hospital.objects.all()
        doctors = DoctorUser.objects.all()
        patients = PatientUser.objects.all()
        context = {
            "userr": user,
            "appointment": app,
            "starttime": timezonify_dt(app.start).strftime("%Y/%m/%d %H:%M"),
            "endtime": timezonify_dt(app.end).strftime("%Y/%m/%d %H:%M"),
            "hospitals": hospitals,
            "doctors": doctors,
            "patients": patients,
            "tab": tabAppUpdate,
            "tabs": getTabs(user_id)
        }
        return context
    else:
        app.title = request.POST["reason"]
        app.start = timezonify_str(request.POST["starttime"])
        app.end = timezonify_str(request.POST["endtime"])
        app.patient = PatientUser.objects.get(user__username=request.POST["patient"])
        app.doctor = DoctorUser.objects.get(user__username=request.POST["doctor"])
        app.hospital = Hospital.objects.get(name=request.POST["hospital"])
        app.save()
        # Logging
        dataLogger = logging.getLogger("dataLogger")
        dataLogger.info(user.get_username() + " updateAppt " + datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M") +
                        " " + app.patient.hospital.name + " patient: " + app.patient.user.username)
        # End logging


@login_required()
def appDelete(request, user_id, app_id):
    user = User.objects.get(pk=user_id)
    Appointment.objects.get(pk=app_id).delete()
    # Logging
    dataLogger = logging.getLogger("dataLogger")
    hospitalName = ""
    try:
        hospitalName = user.hospital.name
    except AttributeError:
        hospitalName = "N/A"
    dataLogger.info(user.get_username() + " deleteAppt " + datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M") +
                    " " + hospitalName + " patient: " + user.username)
    # End logging
    return HttpResponseRedirect("/dash/" + str(user_id) + "/calendar/")


def appValidate(request, user_id):
    doctor = User.objects.get(username=request.GET["doctor"]).doctoruser
    patient = User.objects.get(username=request.GET["patient"]).patientuser
    hospitals = [doctor.hospital.name]
    starttime = timezonify_str(request.GET["starttime"])
    endtime = timezonify_str(request.GET["endtime"])
    appid = int(request.GET["appid"])
    doc_available = True
    pat_available = True
    for app in patient.appointment_set.all():
        if appid != app.id and starttime <= timezonify_dt(app.end) and timezonify_dt(app.start) <= endtime:
            pat_available = False
    for app in doctor.appointment_set.all():
        if appid != app.id and starttime <= timezonify_dt(app.end) and timezonify_dt(app.start) <= endtime:
            doc_available = False
    return JsonResponse({'hospitals': hospitals, 'doc': doc_available, 'pat': pat_available})


def isAdmin(user):
    if user.groups.filter(name='admin').exists():
        return True
    return False


@user_passes_test(isAdmin)
def createEntity(request, user_id):
    user = User.objects.get(pk=user_id)
    admin = AdminUser.objects.get(user=user)
    hospitals = Hospital.objects.all()
    doctors = DoctorUser.objects.all()

    if request.method == 'GET':
        message = ""
        gmessage = ""
        if 'fusern' in request.GET:
            message = "User Name already taken"
        elif 'success' in request.GET:
            gmessage = "User created successfully"
        context = {
            "userr": user,
            "admin": admin,
            "doctors": doctors,
            "hospitals": hospitals,
            "tab": tabCreate,
            "tabs": getTabs(user_id),
            "message": message,
            "good": gmessage
        }
        return render(request, 'Dashboard/dash.html', context)
    else:
        if 'type' not in request.POST:
            hospital = Hospital.objects.create()
            hospital.name = request.POST['name']
            hospital.save()
            # Logging
            dataLogger = logging.getLogger("dataLogger")
            dataLogger.info(user.get_username() + " newHospital " + datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M") +
                            " hospital: " + hospital.name)
            # End logging
        else:
            try:
                newuser = User.objects.create_user(request.POST.get("username"), "dummy@admin.com", request.POST.get("password"))
            except IntegrityError as e:
                return HttpResponseRedirect('/dash/' + str(user.id)+'/create/?fusern')
            newuser.save()
            if request.POST.get("type") == 'Doctor':
                hospital = Hospital.objects.get(name=request.POST.get("yeah"))
                doctor = DoctorUser.create_doctor(newuser, hospital)
                doctor.save()
                # Logging
                dataLogger = logging.getLogger("dataLogger")
                dataLogger.info(
                    user.get_username() + " newDoctor " + datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M") +
                    " " + hospital.name + " doctor: " + doctor.user.username)
                # End logging
            elif request.POST.get("type") == "Nurse":
                doctor = DoctorUser.objects.get(user__username=request.POST.get("doctor"))
                nurse = NurseUser.create_nurse(newuser, doctor)
                nurse.save()
                # Logging
                dataLogger = logging.getLogger("dataLogger")
                dataLogger.info(
                    user.get_username() + " newNurse " + datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M") +
                    " " + nurse.doctor.hospital.name + " nurse: " + nurse.user.username)
                # End logging
            else:
                hospital = Hospital.objects.get(name=request.POST.get("yeah"))
                admin = AdminUser.create_admin(newuser, hospital)
                admin.save()
                # Logging
                dataLogger = logging.getLogger("dataLogger")
                dataLogger.info(
                    user.get_username() + " newAdmin " + datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M") +
                    " " + hospital.name + " admin: " + admin.user.username)
                # End logging
        return HttpResponseRedirect('/dash/' + str(user.id) + '/create/?success')


"""def createAdmin(request, user_id):
    if request.method == 'POST':
        user = User.objects.create_user(request.POST.get("username"), "dummy@admin.com", request.POST.get("password"))
        user.save()
        if request.POST.get("type") == 'Doctor':
            hospital = Hospital.objects.get(name=request.POST.get("yeah"))
            doctor = DoctorUser.create_doctor(user, hospital)
            doctor.save()
        elif request.POST.get("type") == "Nurse":
            doctor = DoctorUser.objects.get(user__username=request.POST.get("doctor"))
            nurse = NurseUser.create_nurse(user, doctor)
            nurse.save()
        else:
            hospital = Hospital.objects.get(name=request.POST.get("yeah"))
            admin = AdminUser.create_admin(user, hospital)

            admin.save()
        user = User.objects.get(pk=user_id)
        return HttpResponseRedirect('/dash/' + str(user.id) + '/')


def createHospital(request, user_id):
    user = User.objects.get(pk=user_id)
    if request.method == 'POST':
        hospital = Hospital.objects.create()
        hospital.name = request.POST.get("name")
        hospital.save()
        return HttpResponseRedirect('/dash/' + str(user.id))


def adminDash(request, user_id):
    user = User.objects.get(pk=user_id)
    admin = AdminUser.objects.get(user=user)
    hospitals = Hospital.objects.all()
    doctors = DoctorUser.objects.all()
    return render(request, 'Dashboard/adminDashboard.html',
                  context={"admin": admin, "hospitals": hospitals, "doctors": doctors})"""


def doctorDash(request, user_id):
    user = User.objects.get(pk=user_id)
    doctor = DoctorUser.objects.get(user=user)
    patients = PatientUser.objects.filter(hospital__in=F('hospital'))
    return render(request, 'Dashboard/doctorDashboard.html', context={"doctor": doctor, "patients": patients})


def doctorView(request, user_id, view_id):
    user = User.objects.get(pk=user_id)
    patient = PatientUser.objects.get(user=user)
    day = datetime.strftime(user.birthday, '%Y-%m-%d')
    return render(request, 'Dashboard/dashboard.html', context={"patient": patient, "birth": day})


def dashHelp(request, user_id):
    return render(request, 'Dashboard/help.html')


"""String to python datetime"""
def timezonify_str(time):
    return timezone.make_aware(datetime.strptime(time, "%Y/%m/%d %H:%M"), timezone.get_current_timezone())


"""Database to local timezone"""
def timezonify_dt(time):
    return time.astimezone(timezone.get_current_timezone())
