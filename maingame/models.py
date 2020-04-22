from django.db import models
from .utils import db_defaults
from django.contrib.auth.models import User

class EventType(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class StatusType(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class UserRole(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Group(models.Model):
    players = models.ManyToManyField(User)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

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
    stakes = models.CharField(max_length=200)

    def __str__(self):
        return self.name

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

    def __str__(self):
        return "User: {} {}, Group: {}, Role: {}".format(
            self.user.first_name,
            self.user.last_name,
            self.group.name,
            self.role.name
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

    def __str__(self):
        return "User: {} {}, Group: {}, Role: {}".format(
            self.user.first_name,
            self.user.last_name,
            self.event.name,
            self.role.name
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
    question = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    multiplier = models.FloatField(default=1)
    status = models.ForeignKey(
        StatusType,
        null=True,
        on_delete=models.SET_NULL
    )

    outcome = models.CharField(
        max_length=200,
        blank=True
    )
    end_time = models.DateTimeField(null=True)

    def __str__(self):
        return self.question

class BetOption(models.Model):
    bet = models.ForeignKey(
        Bet,
        on_delete=models.CASCADE
    )
    text = models.CharField(max_length=200)

    def __str__(self):
        return "{} (Bet: {})".format(
            self.text,
            self.bet.question
        )

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

    def __str__(self):
        option_chosen = self.option.text if self.option else self.custom_option
        return "Bet: {}, {} {}: {}".format(
            self.bet.question,
            self.player.first_name,
            self.player.last_name,
            option_chosen,
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

    def __str__(self):
        return "Bet: {}, {} {}: {}".format(
            self.bet.question,
            self.player.first_name,
            self.player.last_name,
            self.score,
        )

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

    def __str__(self):
        return "Bet: {}, {} {}: Score-{}, Rank-{}".format(
            self.event.name,
            self.player.first_name,
            self.player.last_name,
            self.score,
            self.rank
        )