from django.contrib.postgres.fields import ArrayField
from django.db import models
from .utils.db_enums import StatusType, EventType

# Create your models here.
class User(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    join_date = models.DateTimeField()
    email = models.CharField(max_length=200)
    phone_number = models.IntegerField(
        max_length=12,
        blank=True,
        default=''
    )

class Group(models.Model):
    admin = models.ForeignKey(User)
    players = models.ManyToManyField(User)

class Event(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    type = models.IntegerField(
        choices=EventType.choices(),
        default=EventType.STANDARD
    )
    admin = models.ForeignKey(User)
    players = models.ManyToManyField(User)
    groups = models.ManyToManyField(Group)

class Bet(models.Model):
    created_time = models.DateTimeField()
    question = models.TextField()
    event_id = models.ForeignKey(Event)
    choices = ArrayField(
        models.CharField(),
        default=list,
        null=True
    )
    outcome = models.TextField()
    on_the_line = models.TextField()
    notes = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.IntegerField(
        choices=StatusType.choices(),
        default=StatusType.PENDING
    )
    multiplier = models.FloatField(default=1)

class Placements(models.Model):
    player_id = models.ForeignKey(User)
    bet_id = models.ForeignKey(Bet)
    choice = models.CharField()

class Results(models.Model):
    player_id = models.ForeignKey(User)
    bet_id = models.ForeignKey(Bet)
    event_id = models.ForeignKey(Event)
    score = models.FloatField()
    rank = models.IntegerField()