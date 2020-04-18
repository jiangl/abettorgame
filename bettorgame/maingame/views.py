from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import User, Group, Event, UserGroupRole, UserEventRole, Bet, BetOption, Placement, EventResult, BetResult, EventType, StatusType, UserRole
from django.contrib import messages
import datetime
import pytz
import pdb

#How to render this check to see if user is ADMIN on basetemplate / other pages?
#UserEventRole.objects.get(user=request.user.id, event=event_id))
#can this be done more intelligently with middleware?

def login(request):

    return render(request, 'login.html', {})

def login_user(request):
    try:
      email = request.POST["loginEmail"]
      existing_user = User.objects.get(email=email)
      if existing_user:
        request.session['is_authenticated'] = True

        return HttpResponseRedirect(reverse('index'))

    except (KeyError, User.DoesNotExist):
      # Redisplay the login form.
      return render(request, 'login.html', {'error_message_login': "Hmm, we don't have that email registered. Maybe there was a typo or sign up under 'New User' below!"})
    

def create_user(request):
    email = request.POST["createEmail"]
    existing_user = User.objects.filter(email=email)
    
    if existing_user:
      return render(request, 'login.html', {'error_message_create': "This email is already registered. Please login above!"})
    
    else:
      first_name = request.POST["createFirstName"]
      join_date = datetime.datetime.now().replace(tzinfo=pytz.UTC)

      new_user = User(first_name=first_name, join_date=join_date, email=email)
      new_user.save()

      request.session['is_authenticated'] = True
      return HttpResponseRedirect(reverse('index'))

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
    except (ValueError):
        # Redisplay the question voting form.
        return render(request, 'index.html', {'error_message': "There is no Group with that code."})
    except (KeyError, Event.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'index.html', {'error_message': "There is no Group with that code."})
    except (KeyError, Group.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'index.html', {'error_message': "There is no Group with that code."})
    else:
      return HttpResponseRedirect(reverse('add_bets', args=[group.id, event.id]))

def create_group_and_event(request):
    new_group = Group(name=request.POST["groupName"])
    new_group.save()  

    placeholder_future_start_date = datetime.datetime.now().replace(tzinfo=pytz.UTC) + datetime.timedelta(days=365)
    placeholder_future_end_date = placeholder_future_start_date + datetime.timedelta(days=7)
    placeholder_stakes = 'TBD'

    new_event = Event(start_time=placeholder_future_start_date, end_time=placeholder_future_end_date, name=new_group.name, stakes=placeholder_stakes)
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

def group_admin(request, group_id, event_id):
    event = Event.objects.get(id=event_id)
    group = Group.objects.get(id=group_id)

    is_event_started = event.start_time < datetime.datetime.now().replace(tzinfo=pytz.UTC)
    is_event_ended = event.end_time < datetime.datetime.now().replace(tzinfo=pytz.UTC)
    event_status = {'is_event_started': is_event_started, 'is_event_ended': is_event_ended}

    return render(request, 'group-admin.html', {'event': event, 'group': group, 'event_status': event_status})

def set_stakes(request, group_id, event_id):
    event = Event.objects.get(id=event_id)
    event.stakes = request.POST["setStakes"]

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

    event_commissioner = UserEventRole.objects.get(role=1, event=event.id).user.first_name

    player_first_names = [player.first_name for player in event.players.all()]

    #should this be moved to a method somewhere outside of this file so I can reuse?
    try:
      bets_list = []
      bets = Bet.objects.filter(event=event.id)
      for bet in bets:
        bets_list.append({'bet': bet, 'bet_options': BetOption.objects.filter(bet=bet).order_by('id')})
    except:
      bets_list = None

    return render(request, 'add-bets.html', {'event': event, 'group_id': group_id, 'player_first_names': player_first_names, 'event_commissioner': event_commissioner, 'bets_list': bets_list})

def create_bet(request, group_id, event_id):
    event = Event.objects.get(id=event_id)
    creator = User.objects.get(id=request.user.id)

    #should StatusType ID be 0? but there is no object with an ID of 0
    new_bet = Bet(creator=creator, event=event, created_time=datetime.datetime.now().replace(tzinfo=pytz.UTC), start_time=datetime.datetime.now().replace(tzinfo=pytz.UTC), end_time=datetime.datetime.now().replace(tzinfo=pytz.UTC), question=request.POST['betQuestion'], status=StatusType.objects.get(id=1))
    new_bet.save()

    new_bet_option_1 = BetOption(bet=new_bet, text=request.POST['betOption1'])
    new_bet_option_1.save()

    new_bet_option_2 = BetOption(bet=new_bet, text=request.POST['betOption2'])
    new_bet_option_2.save()

    return HttpResponseRedirect(reverse('add_bets', args=(group_id,event.id,)))

def show_placements(request, group_id, event_id):
    event = Event.objects.get(id=event_id)

    event_commissioner = UserEventRole.objects.get(role=1, event=event.id).user

    # Same comment as in add_bets
    try:
      bets_list = []
      bets = Bet.objects.filter(event=event.id)
      number_of_bets = len(bets)
      for bet in bets:
        bet_options = BetOption.objects.filter(bet=bet).order_by('id')
        bet_options_and_names = []
        for bet_option in bet_options:
          #how to make this check option or custom option depending on the bet?
          bet_option_placements = Placement.objects.filter(bet=bet, option=bet_option)
          if bet_option_placements:
            player_first_names = ', '.join([bet_option.player.first_name for bet_option in bet_option_placements])
            bet_options_and_names.append({'bet_option': bet_option, 'player_first_names': player_first_names})
          else:
            bet_options_and_names.append({'bet_option': bet_option, 'player_first_names': ''})
        bets_list.append({'bet': bet, 'bet_options': bet_options_and_names})
    except:
      bets_list = None


    try:
      players_bets_placed = []
      players_bets_awaiting = []
      for player in event.players.all():
        if len(Placement.objects.filter(player=player)) == number_of_bets:
          players_bets_placed.append(player.first_name)
        else:
          players_bets_awaiting.append(player.first_name)
    except:
      players_bets_placed = []
      players_bets_awaiting = []

    # still need to add placements so they render correctly for each user

    #this is reused code from above - move out into a function?
    is_event_started = event.start_time < datetime.datetime.now().replace(tzinfo=pytz.UTC)
    is_event_ended = event.end_time < datetime.datetime.now().replace(tzinfo=pytz.UTC)
    event_status = {'is_event_started': is_event_started, 'is_event_ended': is_event_ended}

    #replace below logic with authentication and logic in view
    is_admin = event_commissioner.id == request.user.id

    return render(request, 'show-placements.html', {'event': event, 'group_id': group_id, 'event_commissioner': event_commissioner, 'bets_list': bets_list, 'players_bets_placed': players_bets_placed, 'players_bets_awaiting': players_bets_awaiting, 'event_status': event_status, 'is_admin': is_admin})

def create_placements(request, group_id, event_id):
    event = Event.objects.get(id=event_id)
    user = User.objects.get(id=request.user.id)

    # need all the logic here - struggling with the JS working


    return HttpResponseRedirect(reverse('show_placements', args=(group_id,event_id,)))

def leaderboard(request, group_id, event_id):
    event = Event.objects.get(id=event_id)
    event_commissioner = UserEventRole.objects.get(role=1, event=event.id).user

    user = User.objects.get(id=request.user.id)


    return render(request, 'leaderboard.html', {'event': event, 'group_id': group_id, 'event_commissioner': event_commissioner})
















