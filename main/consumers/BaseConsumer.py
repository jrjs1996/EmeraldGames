# chat/consumers.py
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from main.models import SandboxPlayer, Game, SandboxMatch


class BaseConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_sandbox_player(self, sandbox_player_id):
        return SandboxPlayer.objects.get(id=sandbox_player_id)

    @database_sync_to_async
    def get_sandbox_player(self, name, password, game_key):
        sandbox_player = SandboxPlayer.objects.get(name=name, password=password, game__key=game_key)
        return sandbox_player

    @database_sync_to_async
    def get_game(self, game_key):
        game = Game.objects.get(key=game_key)
        return game

    @database_sync_to_async
    def get_sandbox_match(self, match_id):
        sandbox_match = SandboxMatch.objects.get(id=match_id)
        return sandbox_match

    @database_sync_to_async
    def get_match(self, game_key, match_key):
        return SandboxMatch.objects.get(game__key=game_key, key=match_key)

