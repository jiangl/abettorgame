from django.http import HttpResponseRedirect
from django.urls import reverse
from maingame.models import Group, Event, UserGroupRole, UserEventRole, Bet, BetOption, Placement, EventResult, BetResult, EventType, StatusType, UserRole
from django.contrib.auth.models import User
from django.contrib import messages
import datetime
import pytz
from maingame.utils.enums import StatusType, UserRoles
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from maingame.forms import CustomUserCreationForm


#How to render this check to see if user is ADMIN on basetemplate / other pages?
#UserEventRole.objects.get(user=request.user.id, event=event_id))
#can this be done more intelligently with middleware?
def signup(request):
    if request.method == 'POST':
        f = CustomUserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            messages.success(request, 'Account created successfully')
            return HttpResponseRedirect(reverse('maingame:signup'))
    else:
        f = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': f})

def index(request):
  return render(request, 'index.html', {})

@login_required
def join_group_and_event(request):
    try:
      groupAndEventIdArray = request.POST["groupAndEventId"].split('-')
      group = Group.objects.get(id=groupAndEventIdArray[0])
      event = Event.objects.get(id=groupAndEventIdArray[1])

      return HttpResponseRedirect(reverse('maingame:add_bets', args=[group.id, event.id]))

    except:
        # Redisplay the question voting form.
        return render(
          request, 
          'index.html', 
          {
          'error_message': "There is no Group with that code."
          })

@login_required
def create_group_and_event(request):
    new_group = Group.objects.create(name=request.POST["groupName"])

    placeholder_future_start_date = datetime.datetime.now().replace(tzinfo=pytz.UTC) + datetime.timedelta(days=365)
    placeholder_future_end_date = placeholder_future_start_date + datetime.timedelta(days=7)
    placeholder_stakes = '$20, Everyone buys the winner a beer, etc.'

    new_event = Event.objects.create(
      start_time=placeholder_future_start_date, 
      end_time=placeholder_future_end_date, 
      name=new_group.name, 
      stakes=placeholder_stakes
      )

    user = User.objects.get(id=request.user.id)

    new_group.players.add(user)
    new_event.players.add(user)
    new_event.groups.add(new_group)

    role_admin = UserRole.objects.get(id=UserRoles.ADMIN.value)

    UserGroupRole.objects.create(
      user=user, 
      group=new_group, 
      role=role_admin
      )
    
    UserEventRole.objects.create(
      user=user, 
      event=new_event, 
      role=role_admin
      )

    return HttpResponseRedirect(reverse('maingame:group_admin', args=[new_group.id, new_event.id]))

@login_required
def group_admin(request, group_id, event_id):
    event = Event.objects.get(id=event_id)

    is_event_started = event.start_time < datetime.datetime.now().replace(tzinfo=pytz.UTC)
    is_event_ended = event.end_time < datetime.datetime.now().replace(tzinfo=pytz.UTC)

    return render(
      request, 
      'group-admin.html', 
      {
      'event': event, 
      'group_id': group_id, 
      'is_event_started': is_event_started,
      'is_event_ended': is_event_ended
      })

@login_required
def set_stakes(request, group_id, event_id):
    event = Event.objects.get(id=event_id)
    event.stakes = request.POST["setStakes"]
    event.save()

    return HttpResponseRedirect(reverse('maingame:add_bets', args=(group_id,event_id,)))

@login_required
def start_event(request, group_id, event_id):
    event = Event.objects.get(id=event_id)
    event.start_time = datetime.datetime.now().replace(tzinfo=pytz.UTC)
    event.save()

    return HttpResponseRedirect(reverse('maingame:group_admin', args=(group_id,event_id,)))

@login_required
def end_event(request, group_id, event_id):
    event = Event.objects.get(id=event_id)
    event.end_time = datetime.datetime.now().replace(tzinfo=pytz.UTC)
    event.save()

    return HttpResponseRedirect(reverse('maingame:group_admin', args=(group_id,event_id,)))

@login_required
def add_bets(request, group_id, event_id):
    event = Event.objects.get(id=event_id)

    import pdb
    pdb.set_trace()
    event_commissioner = UserEventRole.objects.get(
      role=UserRoles.ADMIN.value, 
      event=event_id
      ).user.first_name

    player_names = [player.first_name for player in event.players.all()]

    #should this be moved to a method somewhere outside of this file so I can reuse?
    try:
      bets_list = [
      {
      'bet': bet, 
      'bet_options': BetOption.objects.filter(bet=bet).order_by('id')
      } 
      for bet in Bet.objects.filter(event=event_id).order_by('id')
      ]

    except:
      bets_list = None

    return render(
      request, 
      'add-bets.html', 
      {
      'event': event, 
      'group_id': group_id, 
      'player_names': player_names, 
      'event_commissioner': event_commissioner, 
      'bets_list': bets_list
      })

@login_required
def create_bet(request, group_id, event_id):
    event = Event.objects.get(id=event_id)

    creator = User.objects.get(id=request.user.id)

    new_bet = Bet.objects.create(
      creator=creator, 
      event=event, 
      created_time=datetime.datetime.now().replace(tzinfo=pytz.UTC), 
      start_time=datetime.datetime.now().replace(tzinfo=pytz.UTC), 
      end_time=datetime.datetime.now().replace(tzinfo=pytz.UTC), 
      question=request.POST['betQuestion'], 
      status_id=1
      )

    BetOption.objects.create(
      bet=new_bet, 
      text=request.POST['betOption1']
      )

    BetOption.objects.create(
      bet=new_bet, 
      text=request.POST['betOption2']
      )

    return HttpResponseRedirect(reverse('maingame:add_bets', args=(group_id,event_id,)))

@login_required
def show_placements(request, group_id, event_id):
    event = Event.objects.get(id=event_id)

    event_commissioner = UserEventRole.objects.get(
      role=2, 
      event=event_id
      ).user

    current_user_firstname = request.user.first_name

    # Same comment as in add_bets
    # Still need to update to nested list comprehenseion
    try:
      bets_list = []
      bets = Bet.objects.filter(event=event_id)

      for bet in bets:
        bet_options = BetOption.objects.filter(bet=bet).order_by('id')
        bet_options_and_names = []
        for bet_option in bet_options:
          #how to make this check option or custom option depending on the bet?
          bet_option_placements = Placement.objects.filter(
            bet=bet, 
            option=bet_option
            )
          if bet_option_placements:
            player_first_names = ', '.join([bet_option.player.first_name for bet_option in bet_option_placements])
            selected = current_user_firstname in player_first_names
            bet_options_and_names.append(
              {
              'bet_option': bet_option, 
              'player_first_names': player_first_names,
              'selected': selected
              })
          else:
            bet_options_and_names.append(
              {
              'bet_option': bet_option, 
              'player_first_names': ''
              })
        bets_list.append(
          {
          'bet': bet, 
          'bet_options': bet_options_and_names
          })

      # should this be updated to use list comprehension? or ternary operator?
      players_bets_placed = []
      players_bets_awaiting = []
      for player in event.players.all():
        if len(Placement.objects.filter(player=player)) == len(bets):
          players_bets_placed.append(player.first_name)
        else:
          players_bets_awaiting.append(player.first_name)

    except:
      bets_list = None
      players_bets_placed = []
      players_bets_awaiting = []

    # still need to add placements so they render correctly for each user

    #this is reused code from above - move out into a function?
    is_event_started = event.start_time < datetime.datetime.now().replace(tzinfo=pytz.UTC)
    is_event_ended = event.end_time < datetime.datetime.now().replace(tzinfo=pytz.UTC)

    #replace below logic with authentication and logic in view
    is_admin = event_commissioner.id == request.user.id

    return render(
      request, 
      'show-placements.html', 
      {
      'event': event, 
      'group_id': group_id, 
      'event_commissioner': event_commissioner, 
      'bets_list': bets_list, 
      'players_bets_placed': players_bets_placed, 
      'players_bets_awaiting': players_bets_awaiting, 
      'is_event_started': is_event_started,
      'is_event_ended': is_event_ended,
      'is_admin': is_admin
      })

@login_required
def create_placements(request, group_id, event_id):
    request_data = request.POST.dict()

    for bet, option in request_data.items():
        if str(bet) != 'csrfmiddlewaretoken':
            Placement.objects.create(
                player = User.objects.get(id=request.user.id),
                bet = Bet.objects.get(id=bet),
                option = BetOption.objects.get(id=option)
            )

    return HttpResponseRedirect(reverse('maingame:show_placements', args=(group_id,event_id)))

@login_required
def leaderboard(request, group_id, event_id):
    event = Event.objects.get(id=event_id)
    event_commissioner = UserEventRole.objects.get(
      role=2, 
      event=event_id
      ).user

    user_first_name = User.objects.get(id=request.user.id).first_name

    bets = Bet.objects.filter(event=event_id)
    number_bets_remaining = len([bet for bet in bets if bet.status.name in ['INITIATED', 'PENDING']])

    # load leaderboard empty stats before game started / first bet finished
    # is there a better way to save this data rather than recalculating from 0 each time?
    bet_results_dict = {}
    for player in event.players.all():
        event_result = EventResult.objects.get(player=player, event=event_id)

        bet_results_dict[player.first_name] = {
            'rank': event_result.rank or 1,
            'score': event_result.score or 0, 
            'won': 0, 
            'lost': 0, 
            'remaining': number_bets_remaining
        }

    # For all completed bets, find the BetResult to count the W/L by player
    bets_completed = [BetResult.objects.filter(bet=bet) for bet in bets if bet.status.name == 'COMPLETED']
    
    for bet in bets_completed:
        player = bet.player.first_name
        if bet.score:
            bet_results_dict[player.won] += 1
        else:
            bet_results_dict[player.lost] += 1

    return render(
      request, 
      'leaderboard.html', 
      {
      'event': event, 
      'group_id': group_id, 
      'event_commissioner': event_commissioner,
      'bet_results_dict': bet_results_dict,
      'user_best_result_dict': bet_results_dict[user_first_name]
      })