import json
import uuid

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels_presence.decorators import touch_presence
from channels_presence.models import Room, Presence
from django.db.models.signals import post_save
from django.dispatch import receiver

from main.actions import sandbox
from main.consumers.BaseConsumer import BaseConsumer
from main.exceptions import serialize_exception, MatchCreationError, InvalidJoinKeyError, InvalidDataError, \
    PlayerInMatchError, PlayerInGameError
from main.middleware import SandboxMiddleware
from main.models import SandboxPlayer, SandboxMatch, SandboxPlayerGroupPlayer
from main.serializers import SandboxPlayerSerializer, SandboxMatchSerializerFull


class ControllerConsumer(BaseConsumer):

    async def connect(self):
        action = "connect"
        try:
            game_key = self.get_credentials_from_headers()
            game = self.get_game(game_key)

            self.game_key = game_key
            self.match_key = None
            self.join_keys = {}
            self.group_name = None
            await self.accept()
            await self.controller_message({
                'action': 'connect',
                'data': {}
            })
        except Exception as e:
            print(e)
            error = json.dumps(serialize_exception(SandboxMiddleware.get_sandbox_exception(e, action)))
            await self.accept()
            await self.send(text_data=error)
            await self.close()

    async def disconnect(self, close_code):
        if self.match_key is not None:
            match = await self.get_match(self.game_key, self.match_key)
            if match.state < 2:
                await self.abort_match(match)
        if self.group_name is not None:
            # Leave room group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        action = ""
        try:
            text_data = json.loads(text_data)
            action = text_data['action']
            data = text_data['data']
            if action == "creatematch":
                wager_amount = data['wager_amount']
                match_type = ""
                if "match_type" in data:
                    match_type = data["match_type"]
                data = await self.create_match(wager_amount, match_type)
                await self.controller_message({
                    'action': action,
                    'data': data
                })
                return
            elif action == "join_match":
                await self.join_match(data)
                return
            elif action == "confirm_join":
                await self.confirm_join(data)
                return
            elif action == "abort_match":
                match = await self.get_match(self.game_key, self.match_key)
                await self.abort_match(match)
                await self.reset_match()
                return
            elif action == "create_player_group":
                await self.create_player_group(data)
                return
            elif action == "end_match":
                await self.end_match(data)
                await self.reset_match()
                return
            elif action == "match_info":
                info = await self.match_info()
                await self.controller_message({
                    'action': 'match_info',
                    'data': info
                })
                return
            elif action == "player_quit":
                await self.player_quit(data)
                return
            elif action == "remove_player_group":
                await self.remove_player_group(data)
                return
            elif action == "start_match":
                await self.start_match()
                return

            raise InvalidDataError("Action not found")
        except Exception as e:
            print(e)
            await self.handle_exception(e, action)

    # Action methods
    async def confirm_join(self, data):
        if 'join_key' not in data.keys():
            raise InvalidJoinKeyError
        join_key = data['join_key']
        if join_key not in self.join_keys.keys():
            raise InvalidJoinKeyError
        sandbox_player_id = self.join_keys[join_key]
        sandbox_player = self.get_sandbox_player(sandbox_player_id)
        sandbox_player_group_name = ""
        if 'group_name' not in data:
            await self.create_solo_player_group(self.game_key, self.match_key, sandbox_player_id)
            sandbox_player_group_name = str(sandbox_player_id)
        else:
            sandbox_player_group_name = data['group_name']
            await self.add_player_to_group(sandbox_player_group_name, sandbox_player_id)

        # Tell the controller the player has been added to the match
        await self.controller_message({
            'action': 'confirm_join',
            'data': {
                'join_key': join_key,
                'player_group': sandbox_player_group_name
            }})

        # Tell the player they have been added to the match
        player_group_name = PlayerConsumer.construct_group_name(sandbox_player_id, self.game_key)
        await self.channel_layer.group_send(
            player_group_name,
            {
                'type': 'confirm_join_message',
                'match_key': self.match_key,
                'action': 'confirm_join',
                'data': {'join_key': join_key,
                         'player_group': sandbox_player_group_name}
            }
        )

    async def join_match(self, data):
        sandbox_player_id = data['id']
        join_key = None
        if sandbox_player_id not in self.join_keys.values():
            join_key = str(uuid.uuid4())
            self.join_keys[join_key] = sandbox_player_id
        else:
            for key, value in self.join_keys.items():
                if value == sandbox_player_id:
                    join_key = key
        player_group_name = PlayerConsumer.construct_group_name(sandbox_player_id, self.game_key)
        await self.channel_layer.group_send(
            player_group_name,
            {
                'type': 'player_message',
                'action': 'join_match',
                'data': {'key': join_key}
            }
        )

    async def create_match(self, wager_amount, match_type=""):
        await self.reset_match()
        match = await self.create_match_action(wager_amount, match_type)
        self.match_key = match['key']
        self.join_keys = {}
        self.group_name = "controller_" + self.match_key + "_" + self.game_key
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        return match

    # Group messages
    async def controller_message(self, event):
        action = event['action']
        data = event['data']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'action': action,
            'data': data
        }))

    # Helpers
    def get_credentials_from_headers(self):
        game_key = ""
        for header in self.scope['headers']:
            header_name = header[0].decode("utf-8")
            if header_name == "game-key":
                game_key = str(header[1].decode("utf-8"))
        return game_key

    @staticmethod
    def construct_group_name(sandbox_match):
        return "controller_" + str(sandbox_match.key) + "_" + sandbox_match.game.key

    async def reset_match(self):
        """
        Checks if this consumer has a current match_key. If it does it checks to see if the match this consumer
        is associated with has ended. If the match hasn't ended it throws an error. If the match has ended it
        removes the match information from this consumer.
        :return:
        """
        if self.match_key is not None:
            match = await self.get_match(self.game_key, self.match_key)
            if match.state < 2:
                raise MatchCreationError("The controllers match cannot be in the Registering or Active state.")
            else:
                self.match_key = None
                self.join_keys = {}
                await self.channel_layer.group_discard(
                    self.group_name,
                    self.channel_name
                )
                self.group_name = None


    @database_sync_to_async
    def abort_match(self, match):
        sandbox.abort_match(self.game_key, match.key)

    @database_sync_to_async
    def add_player_to_group(self, sandbox_player_group_name, sandbox_player_id):
        sandbox.add_player_to_group(self.game_key, self.match_key, sandbox_player_group_name, sandbox_player_id)

    @database_sync_to_async
    def create_match_action(self, wager_amount, match_type):
        match = sandbox.create_match(self.game_key, wager_amount, match_type)
        return match

    @database_sync_to_async
    def create_player_group(self, data):
        group_name = data["group_name"]
        sandbox.create_player_group(self.game_key, self.match_key, group_name)

    @database_sync_to_async
    def create_solo_player_group(self, game_key, match_key, auth_token):
        sandbox.create_solo_player_group(game_key, match_key, auth_token)

    @database_sync_to_async
    def end_match(self, data):
        winning_group_name = data["winning_group_name"]
        sandbox.end_match(self.game_key, self.match_key, winning_group_name)

    @database_sync_to_async
    def match_info(self):
        return sandbox.match_info(self.game_key, self.match_key)

    @database_sync_to_async
    def player_quit(self, data):
        auth_token = data["auth_token"]
        if auth_token is None:
            raise InvalidDataError("Auth token not provided.")
        sandbox.player_quit(self.game_key,self.match_key, auth_token)

    @database_sync_to_async
    def remove_player_group(self, data):
        group_name = data["group_name"]
        sandbox.remove_player_group(self.game_key, self.match_key, group_name)

    @database_sync_to_async
    def start_match(self):
        sandbox.start_match(self.game_key, self.match_key)

    @staticmethod
    @receiver(post_save, sender=SandboxMatch)
    def on_match_save(sender, instance, **kwargs):
        layer = get_channel_layer()
        instance = SandboxMatch.objects.get(id=instance.id)
        group_name = ControllerConsumer.construct_group_name(instance)
        async_to_sync(layer.group_send)(
            group_name,
            {
                'type': 'controller_message',
                'action': 'match_info',
                'data': SandboxMatchSerializerFull(instance).data
            }
        )

    async def handle_exception(self, e, action):
        print(e)
        error = serialize_exception(SandboxMiddleware.get_sandbox_exception(e, action))
        await self.controller_message({
            'action': 'error',
            'data': error
        })


class PlayerConsumer(BaseConsumer):

    async def connect(self):
        action = "authtoken"
        try:
            username, password, game_key = self.get_credentials_from_headers()

            sandbox_player = await self.get_sandbox_player(username, password, game_key)

            self.match_id = None
            self.sandbox_player_key = sandbox_player.id
            self.game_key = game_key
            self.group_name = PlayerConsumer.construct_group_name(sandbox_player.id, game_key)

            in_game = await self.in_game()
            if in_game:
                raise PlayerInGameError

            await self.add_to_room()
            await self.accept()
            await self.player_message({
                'action': 'player_info',
                'data': sandbox.player_info(self.game_key, self.sandbox_player_key)
            })
        except Exception as e:
            print(e)
            await self.accept()
            await self.handle_exception(e, 'connect')
            await self.close()

    async def disconnect(self, close_code):

        # If the player is in a match in this game and the game is
        # in the registering state remove the player from the match
        try:
            sandbox_pgps = SandboxPlayerGroupPlayer.objects.filter(player_id=self.sandbox_player_key,
                                                                   playerGroup__match__game__key=self.game_key,
                                                                   playerGroup__match__state=0,
                                                                   quit=False)
            for sandbox_pgp in sandbox_pgps:
                if sandbox_pgp.playerGroup.match.state == 0:
                    await self.sandbox_player_quit(sandbox_pgp)
        except SandboxPlayerGroupPlayer.DoesNotExist:
            pass
        except Exception as e:
            print(e)
            await self.handle_exception(e, 'disconnect')

        if self.group_name is not None:
            # Leave room group
            await self.leave_room()

    # Receive message from WebSocket
    @touch_presence
    async def receive(self, text_data):
        action = ""
        try:
            message = json.loads(text_data)
            action = message['action']
            message_data = message['data']
            data = ""
            if action == "player_info":
                data = sandbox.player_info(self.game_key, self.sandbox_player_key)
                return
            elif action == "join_match":
                await self.join_match(message_data)
                return

            raise InvalidDataError("Action not found")
        except Exception as e:
            print(e)
            await self.handle_exception(e, action)

    # action methods
    async def join_match(self, data):
        match_id = data['match_id']
        sandbox_match = await self.get_sandbox_match(match_id)
        player = await self.sandbox_player()
        # If the player is already in a match with this game send an error
        if SandboxPlayerGroupPlayer.objects.filter(player=player,
                                                   playerGroup__match__game__key=self.game_key,
                                                   quit=False,
                                                   playerGroup__match__state__lt=2):
            raise PlayerInMatchError
        sandbox_match.player_can_join(player)
        controller_group_name = ControllerConsumer.construct_group_name(sandbox_match)
        await self.channel_layer.group_send(
            controller_group_name,
            {
                'type': 'controller_message',
                'action': 'join_match',
                'data': {
                    'id': self.sandbox_player_key
                }
            }
        )

    # Messages from group
    async def player_message(self, event):
        action = event['action']
        data = event['data']
        await self.send(text_data=json.dumps({
            'action': action,
            'data': data
        }))

    async def confirm_join_message(self, event):
        action = event['action']
        data = event['data']
        match_key = event['match_key']
        match = await self.get_match(self.game_key, match_key)
        data['match_id'] = match.id
        self.match_id = match.id
        await self.player_message({
            'action': event['action'],
            'data': event['data']
        })

    # Helpers
    def get_credentials_from_headers(self):
        username = ""
        password = ""
        game_key = ""
        for header in self.scope['headers']:
            header_name = header[0].decode("utf-8")
            if header_name == "username":
                username = str(header[1].decode("utf-8"))
            elif header_name == "password":
                password = str(header[1].decode("utf-8"))
            elif header_name == "game-key":
                game_key = str(header[1].decode("utf-8"))
        return username, password, game_key

    @staticmethod
    def construct_group_name(player_id, game_key):
        return 'player_%s_%s' % (player_id, game_key)

    # Database helpers
    @database_sync_to_async
    def sandbox_player_quit(self, sandbox_pgp):
        sandbox.player_quit(self.game_key, sandbox_pgp.playerGroup.match.key, self.sandbox_player_key)

    @database_sync_to_async
    def sandbox_player(self):
        sandbox_player = SandboxPlayer.objects.get(id=self.sandbox_player_key)
        return sandbox_player

    @database_sync_to_async
    def add_to_room(self):
        Room.objects.add(self.group_name, self.channel_name)

    @database_sync_to_async
    def in_game(self):
        return Presence.objects.filter(room__channel_name=self.group_name).exists()

    @database_sync_to_async
    def leave_room(self):
        Room.objects.remove(self.group_name, self.channel_name)

    @staticmethod
    @receiver(post_save, sender=SandboxPlayer)
    def on_player_save(sender, instance, **kwargs):
        layer = get_channel_layer()
        group_name = "player_" + str(instance.id) + "_" + str(instance.game.key)
        async_to_sync(layer.group_send)(
            group_name,
            {
                'type': 'player_message',
                'action': 'player_info',
                'data': SandboxPlayerSerializer(instance).data
            }
        )

    async def handle_exception(self, e, action):
        print(e)
        error = serialize_exception(SandboxMiddleware.get_sandbox_exception(e, action))
        await self.player_message({
            'action': 'error',
            'data': error
        })
