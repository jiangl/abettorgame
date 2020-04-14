from django.db import models
from .utils import db_defaults

class EventType(models.Model):
    name = models.TextField()

class StatusType(models.Model):
    name = models.TextField()

class UserRole(models.Model):
    name = models.TextField()

class User(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(
        max_length=200,
        blank=True
    )
    join_date = models.DateTimeField()
    email = models.CharField(max_length=200)
    phone_number = models.IntegerField(
        null=True,
        blank=True
    )

class Group(models.Model):
    players = models.ManyToManyField(User)
    name = models.CharField(max_length=200)

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
    name = models.CharField(max_length=200)
    stakes = models.TextField()

class UserGroupRole(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE
    )
    role = models.ForeignKey(
        UserRole,
        default=db_defaults.set_default_role,
        on_delete=models.SET_DEFAULT
    )

class UserEventRole(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE
    )
    role = models.ForeignKey(
        UserRole,
        default=db_defaults.set_default_role,
        on_delete=models.SET_DEFAULT
    )

class Bet(models.Model):
    creator = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE
    )
    created_time = models.DateTimeField()
    start_time = models.DateTimeField()
    question = models.TextField()
    notes = models.TextField(blank=True)
    multiplier = models.FloatField(default=1)
    status = models.ForeignKey(
        StatusType,
        null=True,
        on_delete=models.SET_NULL
    )

    outcome = models.TextField(blank=True)
    end_time = models.DateTimeField(null=True)

class BetOption(models.Model):
    bet = models.ForeignKey(
        Bet,
        on_delete=models.CASCADE
    )
    text = models.CharField(max_length=200)

class Placement(models.Model):
    player = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING
    )
    bet = models.ForeignKey(
        Bet,
        on_delete=models.CASCADE
    )
    option = models.ForeignKey(
        BetOption,
        null=True,
        on_delete=models.SET_NULL
    )
    custom_option = models.CharField(
        max_length=200,
        blank=True
    )

class BetResult(models.Model):
    player = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    bet = models.ForeignKey(
        Bet,
        on_delete=models.CASCADE
    )
    score = models.FloatField()

class EventResult(models.Model):
    player = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE
    )
    score = models.FloatField()
    rank = models.IntegerField()