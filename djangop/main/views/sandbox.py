"""
Last edited by James Scarrow 2019-01-23
The purpose of the views in this file are to provide an HTTP REST API to access sandbox actions. Each of the views in
this file are actions a user can take. The arguments to the actions are usually sent in post forms. In some cases the
required information is sent in the headers. As is the case when authenticating user.

As of writing this the sockets interface to the actions is currently being implemented. This method of accessing actions
will most likely be replaced by sockets. In which case the url routes to these views should be removed.
"""
from decimal import Decimal

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from main.actions import sandbox


@api_view(['POST'])
def abort_match(request):
    """
    HTTP endpoint for the abort_match action.
    :param request: A post request containing the fields and values for 'gameKey' and 'matchKey'.
    :return: A JSON representation of the match.
    """
    response_data = sandbox.abort_match(request.POST['gameKey'],
                                        request.POST['matchKey'])
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_player_to_group(request):
    """
    HTTP endpoint for the add_player_to_group action.
    :param request: Request containing a POST form with fields and values for 'gameKey, 'matchKey', 'groupName',
    and 'userKey'.
    :return: JSON representation of the sandbox match.
    """
    response_data = sandbox.add_player_to_group(request.POST['gameKey'],
                                                request.POST['matchKey'],
                                                request.POST['groupName'],
                                                request.POST['auth_token'])
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_match(request):
    """
    HTTP endpoint for the create_match action.
    :param request: Request containing the Post fields 'gameKey' containing the key of the game you wish to create a
    dev match for and 'wager' containing the wager amount for the match.
    :return: A JSON representation of the new match.
    """
    response_data = sandbox.create_match(request.POST['gameKey'],
                                         Decimal(request.POST['wager']),
                                         request.POST.get('matchType', ""))
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_player_group(request):
    """
    HTTP endpoint for the create_player_group action.
    :param request: Request containing a POST form with fields and values for 'gameKey', 'matchKey', and 'groupName'
    :return: JSON representation of the sandbox match.
    """
    response_data = sandbox.create_player_group(request.POST['gameKey'],
                                                request.POST['matchKey'],
                                                request.POST['groupName'])
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_solo_player_group(request):
    """
    HTTP endpoint for the create solo_player_group action.
    :param request: Request containing a POST form with fields and values for 'gameKey', 'matchKey', and 'groupName'.
    :return: JSON representation of the sandbox match.
    """
    response_data = sandbox.create_solo_player_group(request.POST['gameKey'],
                                                     request.POST['matchKey'],
                                                     request.POST['auth_token'])
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def end_match(request):
    """
    HTTP endpoint for the end_match action.
    :param request: Request containing a POST form with fields and values for 'gameKey', 'matchKey', and 'groupName'.
    :return: A JSON representation of the match
    """
    response_data = sandbox.end_match(request.POST['gameKey'],
                                      request.POST['matchKey'],
                                      request.POST['groupName'])
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def match_info(request):
    """
    HTTP endpoint for the match_info action.
    :param request: Request containing the POST fields 'gameKey' and 'matchKey.
    :return: A JSON representation of the match.
    """
    response_data = sandbox.match_info(request.POST['matchKey'],
                                       request.POST['gameKey'])
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def obtain_auth_token(request):
    """
    HTTP endpoint for the obtain_auth_token action.
    :param request: Request containing post fields for 'gameKey', 'username', and 'password'.
    :return: JSON representation of the dev players auth token (id)
    """
    response_data = sandbox.obtain_auth_token(request.POST['gameKey'],
                                              request.POST['username'],
                                              request.POST['password'])
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def player_info(request):
    """
    HTTP endpoint for the player_info action.
    :param request: A get request containing the headers 'HTTP_GAMEKEY' and 'HTTP_SANDBOXAUTHORIZATION', with their
    respective values being the game key of the game the sandbox player belongs to and the authentication of the
    sandbox player.
    :return: A JSON representation of the logged in sandbox player.
    """
    response_data = sandbox.player_info(request.META.get("HTTP_GAMEKEY"),
                                        request.META.get("HTTP_SANDBOXAUTHORIZATION")[6:])
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def player_quit(request):
    """
    HTTP endpoint for the player_quit action.
    :param request: A post request containing the fields and values for 'gameKey', 'matchKey' and 'username'
    and their values.
    :return: A JSON representation of the match.
    """
    response_data = sandbox.player_quit(request.POST['gameKey'],
                                        request.POST['matchKey'],
                                        request.POST['auth_token'])
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def remove_player_group(request):
    """
    HTTP endpoint for the remove_player_group action.
    :param request: A post request containing the fields and values for 'gameKey', 'matchKey', and 'groupName' and
    their values
    :return: A JSON representation of the match.
    """
    response_data = sandbox.remove_player_group(request.POST['gameKey'],
                                                request.POST['matchKey'],
                                                request.POST['groupName'])
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def start_match(request):
    """
    HTTP endpoint for the start_match action.
    :param request: Request containing the Post fields 'gameKey' and 'matchKey'.
    :return: A JSON representation of the match.
    """
    response_data = sandbox.start_match(request.POST['gameKey'],
                                        request.POST['matchKey'])
    return Response(response_data, status=status.HTTP_200_OK)

