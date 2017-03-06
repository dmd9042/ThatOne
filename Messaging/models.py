from django.db import models
from Home.models import User

class MessageThread(models.Model):
    sender = models.ForeignKey(User, related_name='sending_user')
    recipient = models.ForeignKey(User, related_name='receiving_user')


class Message(models.Model):
    content = models.CharField(max_length=1000)
    date_time = models.DateTimeField()
    message_thread = models.ForeignKey(MessageThread)
    
