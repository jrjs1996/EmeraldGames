"""
Last edited by James Scarrow 2019-01-23
This file contains the actions that can be taken on sandbox matches. This should contain all of the necessary actions
that can be taken in an Emerald match. It also contains convenience actions that condense multiple actions into a single
one. The docstrings for every function should contain all of the preconditions and postconditions for the actions, which
are enforced at the models level.

The actions level sits between the API and Model level. This is because the primary concern of the API level should be
to communicate with the players and game servers, and the primary concern of the models level should be to define the
data structures and what operations can be performed on them. It is possible for the API level to just call actions on
the models (and it might be a good idea to move these there in the future). Though as of writing I'm currently in the
process of moving from the HTTP REST API to sockets. So my primary objective now is to create actions that can be used
by both the HTTP API and sockets as things transition.
"""
from main.models import *
from main.serializers import *


def abort_match(game_key, match_key):
    """
    Aborts the sandbox match. All of the users will have their money returned to them. This should be used for
    situations like when a dedicated server is disconnected or other unexpected game errors. The match should not
    have already ended.
    :param game_key: The game key of the game the match belongs to.
    :param match_key: The key of the match to abort.
    :return: A JSON representation of the match.
    """
    with transaction.atomic():
        sandbox_match = SandboxMatch.objects.select_for_update().get(game__key=game_key,
                                                                     key=match_key)
        sandbox_match.abort_match()
        data = serialize_match(sandbox_match)
        return data


def add_player_to_group(game_key, match_key, group_name, auth_token):
    """
    Adds the SandboxPlayer to the SandboxPlayerGroup. Returns a JSON representation of the match.
    :param game_key: The game key of the game the match belongs to.
    :param match_key: The match key of the match.
    :param group_name: The name of the group to add the player to.
    :param auth_token: The auth_token of the player to add to the group.
    :return: A JSON representation of the match.
    """
    with transaction.atomic():
        sandbox_match = get_match(game_key, match_key)
        sandbox_player_group = None
        try:
            sandbox_player_group = get_player_group(sandbox_match, group_name)
        except SandboxPlayerGroup.DoesNotExist:
            sandbox_player_group = sandbox_match.create_player_group(group_name)

        sandbox_player = SandboxPlayer.objects.select_for_update().get(id=auth_token)
        sandbox_player_group.add_player(sandbox_player)
        sandbox_match.refresh_from_db()
        data = serialize_match(sandbox_match)
        sandbox_match.save()
        return data


def create_match(game_key, wager, match_type_name=''):
    """
    Creates a new sandbox match and returns a JSON representation of the match. A match type name can be provided to
    create a match with a match type. If a match type name isn't provided, or an empty string is provided, the match
    will be created without a match type.
    :param game_key: Game key for the game to create a sandbox match for.
    :param wager: Wager amount the sandbox match will have
    :param match_type_name: Name of the match type to create the match with.
    :return: A JSON representation of the new sandbox match.
    """
    game = Game.objects.get(key=game_key)

    # If a match type name was provided create a match with that match type
    # otherwise create a match without a match type.
    if match_type_name is None or match_type_name != '':
        match_type = SandboxMatchType.objects.get(game=game, name=match_type_name)
        sandbox_match = SandboxMatch.objects.create(game=game, wager=wager, type=match_type)
    else:
        sandbox_match = SandboxMatch.objects.create(game=game, wager=wager)
    data = serialize_match(sandbox_match)
    return data


def create_player_group(game_key, match_key, group_name):
    """
    Creates a new SandboxPlayerGroup within the given sandbox match. Returns a JSON representation of the match. There
    must not be a player group with the same name in the match.
    :param game_key: The game key of the game the match belongs to.
    :param match_key: The match key of the match.
    :param group_name: The name of the group to be created.
    :return: A JSON representation of the match.
    """
    with transaction.atomic():
        sandbox_match = get_match(game_key=game_key,
                                  match_key=match_key)
        sandbox_match.create_player_group(group_name)
        data = serialize_match(sandbox_match)
        sandbox_match.save()
        return data


def create_solo_player_group(game_key, match_key, auth_token):
    """
    Creates a SandboxPlayerGroup within the given sandbox match. The name of this group will be the name of the given
    sandbox player. This new sandbox group will have the given player in it. There must not be a SandboxPlayerGroup
    with the same name as the player. The player cannot already belong to a SandboxPlayerGroup in the match.
    :param game_key: The game key of the game the match belongs to.
    :param match_key: The match key of the match.
    :param auth_token: The authentication token of the sandbox player to create the group with.
    :return: A JSON representation of the match.
    """
    with transaction.atomic():
        sandbox_match = get_match(game_key, match_key)
        sandbox_player = SandboxPlayer.objects.select_for_update().get(id=auth_token)
        sandbox_player_group = sandbox_match.create_player_group(str(sandbox_player.id))
        sandbox_player_group.add_player(sandbox_player)
        data = serialize_match(sandbox_match)
        sandbox_match.save()
        return data


def end_match(game_key, match_key, winning_group_name):
    """
    Ends the given dev match. This will pay out the winning users. After the match has ended no more actions
    can be performed on the match.
    :param game_key: The game key of the game the match belongs to.
    :param match_key: The match key of the match.
    :param winning_group_name: The name of the player group that won the match.
    :return: A JSON representation of the match.
    """
    with transaction.atomic():
        sandbox_match = SandboxMatch.objects.select_for_update().get(game__key=game_key,
                                                                     key=match_key)
        winning_player_group = get_player_group(sandbox_match, winning_group_name)
        sandbox_match.end_match(winning_player_group)
        data = serialize_match(sandbox_match)
        return data


def match_info(game_key, match_key):
    """
    Returns the sandbox match in JSON format. Contains all of the match details
    :param game_key: The game key of the game the match belongs to.
    :param match_key: The match key of the match.
    :return: A JSON representation of the match.
    """
    sandbox_match = SandboxMatch.objects.get(game__key=game_key, key=match_key)
    data = serialize_match(sandbox_match)
    return data


def obtain_auth_token(game_key, username, password):
    """
    Returns a json representation of the auth token for a sandbox player player. In the case of sandbox players, the id
    is considered the auth token. This makes testing easier. The game key is given so that only the developer that owns
    the sandbox player can access it.
    it.
    :param game_key: Game key for the game that the sandbox player belongs to.
    :param username: Username of the sandbox player.
    :param password: Password of the sandbox player.
    :return: JSON representation of the sandbox players auth token.
    """
    sandbox_player = SandboxPlayer.objects.get(game__key=game_key, name=username, password=password)
    data = {'token': str(sandbox_player.id)}
    return data


def player_info(game_key, sandbox_player_key):
    """
    Returns a JSON representation of the logged in sandbox player. The game key is given so that only the developer that
    owns the sandbox player can access it.
    :param game_key: Game key for the game that the sandbox player belongs to.
    :param sandbox_player_key The key of the sandbox you want the information of.
    :return: A JSON representation of the sandbox player.
    """
    sandbox_player = SandboxPlayer.objects.get(game__key=game_key, id=sandbox_player_key)
    data = SandboxPlayerSerializer(sandbox_player).data
    return data


def player_quit(game_key, match_key, auth_token):
    """
    Removes a player from a given match and returns their wager. This can only happen if the match has not started
    already. The match must be in the registering stage.
    :param game_key: The game key of the game the match belongs to.
    :param match_key: The match key of the match the player will quit.
    :param auth_token: The authentication token of the player to quit the match.
    :return: A JSON representation of the match.
    """
    with transaction.atomic():
        sandbox_match = SandboxMatch.objects.select_for_update().get(game__key=game_key,
                                                                     key=match_key)
        sandbox_player = get_player_in_match(sandbox_match, auth_token)
        sandbox_match.player_quit(sandbox_player)
        data = serialize_match(sandbox_match)
        sandbox_match.save()
        return data


def remove_player_group(game_key, match_key, group_name):
    """
    Removes a player group from the match. The player group must be empty, it cannot contain any players. The match
    must be in the registering state.
    :param game_key: The game key of the game the match belongs to.
    :param match_key: The match key of the match to remove the group from.
    :param group_name: The name of the group to remove.
    :return: A JSON representation of the match.
    """
    with transaction.atomic():
        sandbox_match = get_match(game_key, match_key)
        sandbox_player_group = get_player_group(sandbox_match, group_name)
        sandbox_match.remove_group(sandbox_player_group)
        data = serialize_match(sandbox_match)
        sandbox_match.save()
        return data


def start_match(game_key, match_key):
    """
    Starts a match. Changes the match state to 'Active'. No players can be added to the match and no user groups can be
    created after the match has started. To start the match there must be at least two player groups with at least one
    player in each group.
    :param game_key: The game key of the game the match belongs to.
    :param match_key: The match key of the match to start.
    :return: A JSON representation of the match.
    """
    with transaction.atomic():
        sandbox_match = get_match(game_key, match_key)
        sandbox_match.start_match()
        data = serialize_match(sandbox_match)
        return data


# Helper functions


def get_match(game_key, match_key):
    """
    Gets the match with the given game_key and match_key.
    :param game_key: The game_key of the match to get.
    :param match_key: The match_key of the match to get.
    :return: The specified match.
    """
    return SandboxMatch.objects.select_for_update().get(game__key=game_key, key=match_key)


def get_player_group(match, group_name):
    return SandboxPlayerGroup.objects.select_for_update().get((Q(name=group_name) | Q(type_group__name=group_name)) &
                                                              Q(match=match))


def get_player_in_match(match, auth_token):
    try:
        return SandboxPlayer.objects.select_for_update().get(sandboxplayergroupplayer__playerGroup__match=match,
                                                             id=auth_token)
    except ValueError:
        raise PlayerNotFound()


def serialize_match(sandbox_match):
    sandbox_match.refresh_from_db()
    return SandboxMatchSerializerFull(sandbox_match).data
