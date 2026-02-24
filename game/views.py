from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Player, Role
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@csrf_exempt
def index(request):
    if request.method == "POST":       
        player_id = request.session.get("player_id") 

        if player_id is not None:
            if not Player.objects.filter(id=player_id).exists():
                player_id = None 


        if player_id is None:
            name = request.POST.get("name")
            player = Player(name=name)
            if(Player.objects.count() == 0):
                player.role = "Narrator"

            player.save()

            players = list(Player.objects.values("id", "name", "is_alive", "role"))

            channel_layer = get_channel_layer()


            async_to_sync(channel_layer.group_send)(
                "lobby",  # group name
                {
                    "type": "send_players",  # must match your consumer method
                    "players": players
                }
            )

            request.session["player_id"] = player.id
        else:
            player = Player.objects.get(id=player_id)

        return redirect("lobby")
    return render(request, "game/index.html")

def players_list(request):
    players = list(Player.objects.values("id", "name", "is_alive", "role"))
    return JsonResponse(players, safe=False)

def lobby(request):
    from game.models import Game
    # Get current client
    import random
    player_id = request.session.get("player_id")
    player = Player.objects.get(id=player_id)
    # Load objects
    players = Player.objects.all()
    roles = Role.objects.filter(is_game_role=True)

    # Submit start game form
    if request.method == "POST":
        # Get added roles
        role_ids = request.POST.getlist("roles")
        game = Game.objects.first()

        if not game:
            game = Game.objects.create()
        game.selected_roles = role_ids
        game.current_role = None
        game.save()

        shuffled_roles = random.sample(role_ids, k=len(role_ids))

        # Randomly assign roles, except for narrator
        assignable_players = [p for p in players if p.role != "Narrator"]
        for player, role_id in zip(assignable_players, shuffled_roles):
            role = Role.objects.get(id=role_id)
            player.role = role.name 
            player.save()
            
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "lobby",
            {"type": "start_game"}
        )
        return redirect("game")
        


    return render(request, "game/lobby.html", {"player": player, "players": players, "roles": roles})

def game(request):
    from game.models import Game
    player_id = request.session.get("player_id")
    print("player_id:", player_id)

    player = Player.objects.get(id=player_id)
    players = Player.objects.all()
    roleObjects = Role.objects.all()
    game = Game.objects.first()
    role_ids = game.selected_roles
    roles = [Role.objects.get(id=r) for r in role_ids]
    
    high_mafia = max(roles, key=lambda r: r.mafia_priority, default=None)


    if request.method == "POST":

        action = request.POST.get("action")
        channel_layer = get_channel_layer()
        
        #region Actions 
        if action == "mafia_kill":
            target_id = request.POST.get("target_id")
            print("Mafia targeted:", target_id)
            Player.objects.get(id=target_id).attacked = True

        elif action == "doctor_heal":
            target_id = request.POST.get("target_id")
            print("Doctor healed:", target_id)
            Player.objects.get(id=target_id).protected = True

        # Change
        elif action == "investigator_investigate":
            target_id = request.POST.get("target_id")
            print("Exec chose:", target_id)
            player_choice = Player.objects.get(id=target_id)
            if(player_choice.protection_level < 1):
                player_choice.role = "Vampire"

        # Change
        elif action == "medium_seance":
            target_id = request.POST.get("target_id")
            print("Exec chose:", target_id)
            player_choice = Player.objects.get(id=target_id)
            if(player_choice.protection_level < 1):
                player_choice.role = "Vampire"

        # Change
        elif action == "sheriff_investigate":
            target_id = request.POST.get("target_id")
            print("Exec chose:", target_id)
            player_choice = Player.objects.get(id=target_id)
            if(player_choice.protection_level < 1):
                player_choice.role = "Vampire"

        elif action == "vigilante_shot":
            target_id = request.POST.get("target_id")
            print("Exec chose:", target_id)
            player_choice = Player.objects.get(id=target_id)
            if(player_choice.protection_level < 1):
                player_choice.attacked = True

        # Change
        elif action == "decoy_decoy":
            target_id = request.POST.get("target_id")
            print("Exec chose:", target_id)
            player_choice = Player.objects.get(id=target_id)
            if(player_choice.protection_level < 1):
                player_choice.role = "Vampire"

        # Change
        elif action == "transporter_transport":
            target_id = request.POST.get("target_id")
            print("Exec chose:", target_id)
            player_choice = Player.objects.get(id=target_id)
            if(player_choice.protection_level < 1):
                player_choice.role = "Vampire"

            # Change
        elif action == "veteran_alert":
            target_id = request.POST.get("target_id")
            print("Exec chose:", target_id)
            player_choice = Player.objects.get(id=target_id)
            if(player_choice.protection_level < 1):
                player_choice.role = "Vampire"

        elif action == "blackmailer_blackmail":
            target_id = request.POST.get("target_id")
            print("Exec chose:", target_id)
            player_choice = Player.objects.get(id=target_id)
            player_choice.blackmailed = True

        # Change
        elif action == "consigliere_investigate":
            target_id = request.POST.get("target_id")
            print("Exec chose:", target_id)
            player_choice = Player.objects.get(id=target_id)
            if(player_choice.protection_level < 1):
                player_choice.role = "Vampire"

        elif action == "janitor_clean":
            target_id = request.POST.get("target_id")
            print("Exec chose:", target_id)
            player_choice = Player.objects.get(id=target_id)
            player_choice.cleaned = True

        # Change
        elif action == "framer_frame":
            target_id = request.POST.get("target_id")
            print("Exec chose:", target_id)
            player_choice = Player.objects.get(id=target_id)
            if(player_choice.protection_level < 1):
                player_choice.role = "Vampire"

        # Change
        elif action == "saboteur_sabotage":
            target_id = request.POST.get("target_id")
            print("Exec chose:", target_id)
            player_choice = Player.objects.get(id=target_id)
            if(player_choice.protection_level < 1):
                player_choice.role = "Vampire"

        elif action == "sk_kill":
            target_id = request.POST.get("target_id")
            player_choice = Player.objects.get(id=target_id)
            print("SK chose:", player_choice.name)
            if(player_choice.protection_level < 1):
                player_choice.attacked = True
            
        elif action == "hypnotist_hypnotize":
            print("")
         
        elif action == "amnesiac_remember":
            print("")
         
        elif action == "vampire_bite":
            target_id = request.POST.get("target_id")
            player_choice = Player.objects.get(id=target_id)
            print("Vamp chose:", player_choice.name)
            if(player_choice.protection_level < 1):
                player_choice.role = "Vampire"
         
        elif action == "werewolf_attack":
            target_id = request.POST.get("target_id")
            player_choice = Player.objects.get(id=target_id)
            print("Werewolf chose:", player_choice.name)
            if(player_choice.protection_level < 1):
                player_choice.attacked = True

         
        elif action == "witch_curse":
            target_id = request.POST.get("target_id")
            player_choice = Player.objects.get(id=target_id)
            print("Witch chose:", player_choice.name)
            player_choice.cursed = True
            # Check witch targets

        elif action == "executioner_target":
            target_id = request.POST.get("target_id")
            player_choice = Player.objects.get(id=target_id)
            print("Exec chose:", player_choice.name)
            player_choice.executionerID = player_id
        
        #endregion    

        elif action == "advance_phase":
            async_to_sync(channel_layer.group_send)(
                "game",
                {
                    "type": "advance_night"
                }
            )

    return render(request, "game/game.html", {
        "player": player, 
        "players": players, 
        "roles": roles, 
        "game": game,
        "high_mafia": high_mafia
    })

