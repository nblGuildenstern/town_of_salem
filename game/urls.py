from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("lobby/", views.lobby, name="lobby"),
    path("game/", views.game, name="game"),
    path("players/", views.players_list, name="players_list")
]