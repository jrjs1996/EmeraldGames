from rest_framework import serializers

from main.models import User, Game, Match, PlayerGroup, Player, SandboxPlayer, SandboxMatch, SandboxPlayerGroup


# This is the serializer class

# class SnippetSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     title = serializers.CharField(required=False, allow_blank=True, max_length=100)
#     code = serializers.CharField(style={'base_template': 'textarea.html'})
#     linenos = serializers.BooleanField(required=False)
#     language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, default='python')
#     style = serializers.ChoiceField(choices=STYLE_CHOICES, default='friendly')
#
#     def create(self, validated_data):
#         """
#         Create and return a new `Snippet` instance, given the validated data.
#         """
#         return Snippet.objects.create(**validated_data)
#
#     def update(self, instance, validated_data):
#         """
#         Update and return an existing `Snippet` instance, given the validated data.
#         """
#         instance.title = validated_data.get('title', instance.title)
#         instance.code = validated_data.get('code', instance.code)
#         instance.linenos = validated_data.get('linenos', instance.linenos)
#         instance.language = validated_data.get('language', instance.language)
#         instance.style = validated_data.get('style', instance.style)
#         instance.save()
#         return instance

# This does the same thing with the modelserializer class


class UserBalanceSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = User
        fields = ('steamId', 'balance')


class UserWagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('steamId', 'wager')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'balance', 'auth_token')


class PlayerSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email', read_only=True)
    balance = serializers.CharField(source='user.balance', read_only=True)
    auth_token = serializers.CharField(source='user.auth_token', read_only=True)

    class Meta:
        model = Player
        fields = ('email', 'balance', 'auth_token', 'first_name', 'last_name')


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('name',)


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ('key',)


class PlayerGroupSerializer(serializers.ModelSerializer):
    users = UserSerializer(read_only=True, source="player_set", many=True)

    class Meta:
        model = PlayerGroup
        fields = ('name', 'users',)


class MatchSerializerFull(serializers.ModelSerializer):
    userGroups = PlayerGroupSerializer(read_only=True, source="playergroup_set", many=True)

    class Meta:
        model = Match
        fields = ('pool', 'key', 'date_created', 'date_finished', 'userGroups', 'key', 'wager')


# ---------------------------------------------------------- Sandbox ---------------------------------------------------


class SandboxPlayerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='name', read_only=True)
    auth_token = serializers.CharField(source='id')

    class Meta:
        model = SandboxPlayer
        fields = ('username', 'balance', 'auth_token')


class SandboxPlayerGroupSerializer(serializers.ModelSerializer):
    players = SandboxPlayerSerializer(source='getPlayers', many=True, read_only=True)
    name = serializers.CharField(source='get_name')

    class Meta:
        model = SandboxPlayerGroup
        fields = ('name', 'players',)


class SandboxPlayerSerializerController(serializers.ModelSerializer):
    username = serializers.CharField(source='name', read_only=True)
    auth_token = serializers.CharField(source='id')

    class Meta:
        model = SandboxPlayer
        fields = ('username', 'auth_token')


class SandboxPlayerGroupSerializerController(serializers.ModelSerializer):
    players = SandboxPlayerSerializerController(source='getPlayers', many=True, read_only=True)
    name = serializers.CharField(source='get_name')

    class Meta:
        model = SandboxPlayerGroup
        fields = ('name', 'players',)


class SandboxMatchSerializerFull(serializers.ModelSerializer):
    playerGroups = SandboxPlayerGroupSerializerController(source='get_player_groups', many=True, read_only=True)

    class Meta:
        model = SandboxMatch
        fields = ('id','state', 'pool', 'key', 'date_created', 'date_started', 'date_finished', 'playerGroups', 'wager')

