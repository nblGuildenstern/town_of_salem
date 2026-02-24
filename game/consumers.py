import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from .models import Player
        self.player_id = self.scope['query_string'].decode().split("player_id=")[1]

        await sync_to_async(Player.objects.get_or_create)(
            id=self.player_id,
            defaults={"name": f"Player {self.player_id}"}
        )

        await self.channel_layer.group_add("lobby", self.channel_name)
        await sync_to_async(self.set_online)(True)
        await self.accept()

        await self.broadcast_players()

    async def disconnect(self, close_code):
        from .models import Player 
        await self.channel_layer.group_discard("lobby", self.channel_name)
        await sync_to_async(self.set_online)(False)
        await self.broadcast_players()

    async def send_players(self, event):
        players = event["players"]
        await self.send(text_data=json.dumps({
        "type": "players_update",
        "players": players
    }))

    async def broadcast_players(self):
        from .models import Player
        players = await sync_to_async(list)(
            Player.objects.values("id", "name", "is_alive", "role")
        )
        await self.channel_layer.group_send(
            "lobby",
            {"type": "send_players", "players": players}
        )

    async def receive_json(self, content):
        if content.get("action") == "clear_lobby":
            from django.db.models import F
            from asgiref.sync import sync_to_async
            # delete all players
            await sync_to_async(Player.objects.all().delete)()
            # broadcast empty list
            await self.channel_layer.group_send(
                "lobby",
                {"type": "send_players", "players": []}
            )

    def set_online(self, status):
        from .models import Player
        player = Player.objects.get(id=self.player_id)
        player.is_online = status
        player.save()

    async def start_game(self, event):
        await self.send(text_data=json.dumps({
            "type": "start_game"
        }))

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.player_id = self.scope['query_string'].decode().split("player_id=")[1]
        await self.channel_layer.group_add("game", self.channel_name)
        await sync_to_async(self.set_online)(True)
        await self.accept()
        await self.broadcast_players()

    async def disconnect(self, close_code):
        from .models import Player 
        await self.channel_layer.group_discard("game", self.channel_name)
        await sync_to_async(self.set_online)(False)
        await self.broadcast_players()

    def set_online(self, status):
        from .models import Player
        player = Player.objects.get(id=self.player_id)
        player.is_online = status
        player.save()

    async def send_players(self, event):
        from .models import Player

        players = event["players"]

        me = await sync_to_async(Player.objects.get)(id=self.player_id)

        await self.send(text_data=json.dumps({
            "type": "players_update",
            "players": players,
            "player": {
                "id": me.id,
                "role": me.role
            }
        }))

    async def broadcast_players(self):
        from .models import Player
        players = await sync_to_async(list)(
            Player.objects.values("id", "name", "is_alive", "role")
        )

        await self.channel_layer.group_send(
            "game",
            {"type": "send_players", "players": players}
        )

    async def advance_night(self, event):
        from .models import Game
        print("firing")
        game = await sync_to_async(Game.objects.first)()

        await sync_to_async(game.advance_night_role)()
        game = await sync_to_async(Game.objects.get)(id=game.id)

        role_name = None
        if game.current_role_id:  # check FK id first
            role_name = await sync_to_async(lambda: game.current_role.name)()

        await self.send(text_data=json.dumps({
            "type": "advance_night",
            "phase": game.current_phase,
            "role": role_name
        }))