from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('join-group-and-event', views.join_group_and_event, name='join_group_and_event'),
    path('create-group-and-event', views.create_group_and_event, name='create_group_and_event'),
    path('<int:group_id>/<int:event_id>/group-admin', views.group_admin, name='group_admin'),
    path('<int:group_id>/<int:event_id>/set-stakes', views.set_stakes, name='set_stakes'),
    path('<int:group_id>/<int:event_id>/add-bets', views.add_bets, name='add_bets'),
    path('<int:group_id>/<int:event_id>/start-event', views.start_event, name='start_event'),
    path('<int:group_id>/<int:event_id>/end-event', views.end_event, name='end_event'),
    path('show-placements', views.show_placements, name='show_placements'),
    path('leaderboard', views.leaderboard, name='leaderboard'),
]