from django.shortcuts import render

from .models import Appointment

# Create your views here.
def calendarView(request, user_id):
    context = {
        "appointments": Appointment.objects.all()
    }
    return render(request, 'Calenda/calendar.html', context)