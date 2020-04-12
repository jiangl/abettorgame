from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('join-group', views.join_group, name='join_group'),
    path('create-group', views.create_group, name='create_group'),
    path('group-admin', views.group_admin, name='group_admin'),
    path('add-bets', views.add_bets, name='add_bets'),
    path('show-placements', views.show_placements, name='show_placements'),
    path('leaderboard', views.leaderboard, name='leaderboard'),
]