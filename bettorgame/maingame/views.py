from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import User, Group, Event, UserGroupRole, UserEventRole, Bet, BetOption, Placement, Result, EventType, StatusType, UserRole
from django.contrib import messages
import datetime
import pytz
import pdb

#How to render this check to see if user is ADMIN on basetemplate / other pages?
#UserEventRole.objects.get(user=request.user.id, event=event_id))
#can this be done more intelligently with middleware?

def index(request):
  #Q: how can we apply this to every page without putting the logic in ever view
  # if request.user.is_authenticated:
  return render(request, 'index.html', {})
  # else:
  #   return render(request, 'login.html', {})

def join_group_and_event(request):
    try:
      groupAndEventIdArray = request.POST["groupAndEventId"].split('-')
      group = Group.objects.get(id=groupAndEventIdArray[0])
      event = Event.objects.get(id=groupAndEventIdArray[1])
    except (KeyError, Event.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'index.html', {'error_message': "There is no Group with that ID."})
    else:
      #connect user to group/event
      request.session['is_admin'] = "ADMIN" == UserEventRole.objects.get(user=request.user.id, event=event.id)

      return HttpResponseRedirect(reverse('add_bets', args=[group.id, event.id]))

def create_group_and_event(request):
    new_group = Group(name=request.POST["groupName"])
    new_group.save()  

    placeholder_future_start_date = datetime.datetime.now().replace(tzinfo=pytz.UTC) + datetime.timedelta(days=365)
    placeholder_future_end_date = placeholder_future_start_date + datetime.timedelta(days=7)

    new_event = Event(start_time=placeholder_future_start_date, end_time=placeholder_future_end_date, name=new_group.name)
    new_event.save()

    user = User.objects.get(id=request.user.id)

    new_group.players.add(user)
    new_event.players.add(user)
    new_event.groups.add(new_group)

    role_admin = UserRole.objects.get(id=1)

    group_commissioner = UserGroupRole(user=user, group=new_group, role=role_admin)
    group_commissioner.save()
    
    event_commissioner = UserEventRole(user=user, event=new_event, role=role_admin)
    event_commissioner.save()

    request.session['is_admin'] = True

    return HttpResponseRedirect(reverse('group_admin', args=[new_group.id, new_event.id]))

def login(request):

    return render(request, 'login.html', {})

def group_admin(request, group_id, event_id):
    event = Event.objects.get(id=event_id)
    group = Group.objects.get(id=group_id)

    is_event_started = event.start_time < datetime.datetime.now().replace(tzinfo=pytz.UTC)
    is_event_ended = event.end_time < datetime.datetime.now().replace(tzinfo=pytz.UTC)
    event_status = {'is_event_started': is_event_started, 'is_event_ended': is_event_ended}

    return render(request, 'group-admin.html', {'event': event, 'group': group, 'event_status': event_status})

def set_stakes(request, group_id, event_id):
    event = Event.objects.get(id=event_id)
    # NEED TO UPDATE MODEL TO HAVE STAKES ON EVENT
    # stakes = request.POST["setStakes"]
    # event.stakes = stakes
    return HttpResponseRedirect(reverse('add_bets', args=(group_id,event.id,)))

def start_event(request, group_id, event_id):
    event = Event.objects.get(id=event_id)
    event.start_time = datetime.datetime.now()

    return HttpResponseRedirect(reverse('group_admin', args=(group_id,event.id,)))

def end_event(request, group_id, event_id):
    event = Event.objects.get(id=event_id)

    event.end_time = datetime.datetime.now().replace(tzinfo=pytz.UTC)

    return HttpResponseRedirect(reverse('group_admin', args=(group_id,event.id,)))

def add_bets(request, group_id, event_id):
    event = Event.objects.get(id=event_id)

    #admin_role = UserRole.objects.get(name="ADMIN")
    #how to access the enum?
    #event_commissioner = UserEventRole.objects.get(role="ADMIN", event=event.id)

    player_first_names = [player.first_name for player in event.players.all()]

    return render(request, 'add-bets.html', {'event': event, 'group_id': group_id, 'player_first_names': player_first_names}) #'event_commissioner': event_commissioner

def show_placements(request):

    return render(request, 'show-placements.html', {})

def leaderboard(request):

    return render(request, 'leaderboard.html', {})