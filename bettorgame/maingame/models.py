from django.contrib.postgres.fields import ArrayField
from django.db import models
from .utils import db_defaults

class EventType(models.Model):
    name = models.TextField()

class StatusType(models.Model):
    name = models.TextField()

class UserRoles(models.Model):
    name = models.TextField()

class User(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    join_date = models.DateTimeField()
    email = models.CharField(max_length=200)
    phone_number = models.IntegerField(
        blank=True,
        default=''
    )

class Group(models.Model):
    players = models.ManyToManyField(User)

class Event(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    type = models.ForeignKey(
        EventType,
        null=True,
        on_delete=models.SET_NULL
    )
    players = models.ManyToManyField(User)
    groups = models.ManyToManyField(Group)


class UserGroupRoles(models.Model):
    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    group_id = models.ForeignKey(
        Group,
        on_delete=models.CASCADE
    )
    role = models.ForeignKey(
        UserRoles,
        default=db_defaults.set_default_role,
        on_delete=models.SET_DEFAULT
    )

class UserEventRoles(models.Model):
    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    event_id = models.ForeignKey(
        Event,
        on_delete=models.CASCADE
    )
    role = models.ForeignKey(
        UserRoles,
        default=db_defaults.set_default_role,
        on_delete=models.SET_DEFAULT
    )

class Bet(models.Model):
    created_time = models.DateTimeField()
    question = models.TextField()
    event_id = models.ForeignKey(
        Event,
        on_delete=models.CASCADE
    )
    options = ArrayField(
        models.CharField(max_length=200),
        default=list,
        null=True
    )
    outcome = models.TextField()
    on_the_line = models.TextField()
    notes = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.ForeignKey(
        StatusType,
        null=True,
        on_delete=models.SET_NULL
    )
    multiplier = models.FloatField(default=1)

class Placements(models.Model):
    player_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    bet_id = models.ForeignKey(
        Bet,
        on_delete=models.CASCADE
    )
    answer = models.CharField(max_length=200)

class Results(models.Model):
    player_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    bet_id = models.ForeignKey(
        Bet,
        on_delete=models.CASCADE
    )
    event_id = models.ForeignKey(
        Event,
        on_delete=models.CASCADE
    )
    score = models.FloatField()
    rank = models.IntegerField()