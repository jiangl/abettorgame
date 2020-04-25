from django.http import HttpResponseRedirect
from django.urls import reverse
from maingame.models import Group, Event, EventStage, UserGroupRole, UserEventRole, Bet, BetOption, Placement, EventResult, BetResult, EventType, StatusType, UserRole
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
import datetime
import pytz
from maingame.utils.enums import StatusType, UserRoles
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from maingame.forms import CustomUserCreationForm
from maingame.utils.enums import EventType, StandardEventStages


def signup(request):
    if request.method == 'POST':
        f = CustomUserCreationForm(request.POST)
        if f.is_valid():
            try:
                f.save()
                new_user = authenticate(username=f.cleaned_data['email'], 
                                        password=f.cleaned_data['password1']
                                        )
                login(request, new_user)
                return HttpResponseRedirect(reverse('maingame:index'))
            except:
                messages.add_message(request, messages.ERROR, 'There is already an account created with %s.' % f.cleaned_data['email'])
                f = CustomUserCreationForm()
                return render(request, 'signup.html', {'form': f})
    else:
        f = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': f})

@login_required
def index(request):
  return render(request, 'index.html', {})

@login_required
def join_group_and_event(request):
    try:
      groupAndEventIdArray = request.POST["groupAndEventId"].split('-')
      group = Group.objects.get(id=groupAndEventIdArray[0])
      event = Event.objects.get(id=groupAndEventIdArray[1])

      group.players.add(request.user)
      event.players.add(request.user)

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
    placeholder_stakes = 'TBD'

    new_event = Event.objects.create(
        start_time=placeholder_future_start_date,
        end_time=placeholder_future_end_date,
        name=new_group.name,
        stakes=placeholder_stakes,
        type_id=EventType.STANDARD.value
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
    allow_set_stakes = False
    allow_lock_bets = False
    allow_start_game = False
    allow_end_game = False

    current_stage_id = event.current_stage.id if event.current_stage else None
    event_type_id = event.type.id

    if event_type_id is EventType.STANDARD.value:
        if current_stage_id is None:
            allow_set_stakes = True
        else:
            if current_stage_id is not StandardEventStages.END.value:
                allow_end_game = True
            if current_stage_id is StandardEventStages.ADD.value:
                allow_lock_bets = True
            elif current_stage_id is StandardEventStages.PLACE.value:
                allow_start_game = True

    return render(
        request,
        'group-admin.html',
        {
            'event': event,
            'group_id': group_id,
            'allow_set_stakes': allow_set_stakes,
            'allow_lock_bets': allow_lock_bets,
            'allow_start_game': allow_start_game,
            'allow_end_game': allow_end_game
        })

@login_required
def set_stakes(request, group_id, event_id):
    event = Event.objects.get(id=event_id)
    event.stakes = request.POST["setStakes"]

    if event.type.id is EventType.STANDARD.value:
        event.current_stage = EventStage.objects.get(id=StandardEventStages.ADD.value)
    event.save()

    return HttpResponseRedirect(reverse('maingame:add_bets', args=(group_id, event_id)))

@login_required
def lock_bets(request, group_id, event_id):
    event = Event.objects.get(id=event_id)
    if event.type.id is EventType.STANDARD.value:
        event.current_stage_id = StandardEventStages.PLACE.value
    event.save()

    return HttpResponseRedirect(reverse('maingame:group_admin', args=(group_id, event_id)))

@login_required
def start_event(request, group_id, event_id):
    event = Event.objects.get(id=event_id)
    event.start_time = datetime.datetime.now().replace(tzinfo=pytz.UTC)
    if event.type.id is EventType.STANDARD.value:
        event.current_stage_id = StandardEventStages.RUN.value
    event.save()

    return HttpResponseRedirect(reverse('maingame:group_admin', args=(group_id, event_id)))

def end_all_bets(event_id):
    bets_for_event = Bet.objects.filter(event_id=event_id)
    for bet in bets_for_event:
        bet.status_id = StatusType.COMPLETED.value
        bet.end_time = datetime.datetime.now().replace(tzinfo=pytz.UTC)
        bet.outcome = None
        bet.save()

@login_required
def end_event(request, group_id, event_id):
    event = Event.objects.get(id=event_id)
    event.end_time = datetime.datetime.now().replace(tzinfo=pytz.UTC)
    if event.type.id is EventType.STANDARD.value:
        event.current_stage_id = StandardEventStages.END.value

    end_all_bets(event_id)
    event.save()

    return HttpResponseRedirect(reverse('maingame:group_admin', args=(group_id, event_id)))

@login_required
def add_bets(request, group_id, event_id):
    event = Event.objects.get(id=event_id)
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
      status_id=StatusType.PENDING.value
      )

    BetOption.objects.create(
      bet=new_bet, 
      text=request.POST['betOption1']
      )

    BetOption.objects.create(
      bet=new_bet, 
      text=request.POST['betOption2']
      )

    return HttpResponseRedirect(reverse('maingame:add_bets', args=(group_id, event_id)))

@login_required
def show_placements(request, group_id, event_id):
    event = Event.objects.get(id=event_id)

    event_commissioner = UserEventRole.objects.get(
      role=UserRoles.ADMIN.value, 
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

    for bet_id, option_id in request_data.items():
        if str(bet_id) != 'csrfmiddlewaretoken':
            placement, created = Placement.objects.get_or_create(
                player_id = request.user.id,
                bet_id = bet_id
            )
            placement.option_id = option_id
            placement.save()

    return HttpResponseRedirect(reverse('maingame:show_placements', args=(group_id, event_id)))

@login_required
def admin_bet_result(request, group_id, event_id):
    request_data = request.POST.dict().get('selection')
    bet_and_option_ids = request_data.split("-")

    bet = Bet.objects.get(id=bet_and_option_ids[0])
    bet.outcome = BetOption.objects.get(id=bet_and_option_ids[1]).text
    bet.status_id = StatusType.COMPLETED.value
    bet.end_time = datetime.datetime.now().replace(tzinfo=pytz.UTC)
    bet.save()

    return HttpResponseRedirect(reverse('maingame:running_bets', args=(group_id, event_id)))

@login_required
def running_bets(request, group_id, event_id):
    event = Event.objects.get(id=event_id)

    event_commissioner = UserEventRole.objects.get(
      role=UserRoles.ADMIN.value,
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
        bet_outcome = bet.outcome
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
              'selected': selected,
              'is_outcome': bet_outcome == bet_option.text
              })
          else:
            bet_options_and_names.append(
              {
              'bet_option': bet_option,
              'player_first_names': '',
              'is_outcome': bet_outcome == bet_option.text
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
    usergrouprole = UserGroupRole.objects.get(user=request.user.id, group=group_id)
    role_id = usergrouprole.role.id
    is_admin = (role_id == UserRoles.ADMIN.value)

    return render(
      request,
      'running-bets.html',
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
def leaderboard(request, group_id, event_id):
    event = Event.objects.get(id=event_id)
    event_commissioner = UserEventRole.objects.get(
      role=UserRoles.ADMIN.value, 
      event=event_id
      ).user.first_name

    user_first_name = request.user.first_name

    bets = Bet.objects.filter(event=event_id)
    number_bets_remaining = len([bet for bet in bets if bet.status.name in ['INITIATED', 'PENDING']])

    # load leaderboard empty stats before game started / first bet finished
    # is there a better way to save this data rather than recalculating from 0 each time?
    bet_results_dict = {}
    event_result = None
    for player in event.players.all():
        try:
            event_result = EventResult.objects.get(player=player, event=event_id)
        except:
            pass

        bet_results_dict[player.first_name] = {
            'rank': event_result.rank if event_result else 1,
            'score': event_result.score if event_result else 0, 
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