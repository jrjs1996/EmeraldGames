from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from main import serializers
from main.exceptions import UserAnonymousException, UserNotPlayerException
from main.models import User, Game, Match, PlayerGroup, PlayerGroupPlayer


@api_view(['GET', 'POST'])
def get_user(request):
    """
    Returns a JSON representation of the specified user.
    :param request: A Get request with a username in the url like so .../getuser/{username}/ or
    a post request containing a 'username' field and value.
    :return: JSON representation of the specified user.
    """
    if request.method == 'GET':
        # Get the user
        user = User.objects.get(email=request.GET['username'])
        # Serialize the user
        serializer = serializers.UserSerializer(user)
        # Send the response
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        # Get the user
        user = User.objects.get(email=request.POST['username'])
        # Serialize the user
        serializer = serializers.UserSerializer(user)
        # Send the response
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_user(request):
    """
    Creates a user with the specified information.
    :param request: Post form containing the fields 'email', 'first_name', 'last_name', and 'password' and their values
    :return: Status 200 if the operation was successful.
    """
    # Get signup information
    email = request.POST['email']
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    password = request.POST['password']
    # Create a new user with the specified information
    user = User.objects.create(email=email,
                               first_name=first_name,
                               last_name=last_name,
                               password=password)
    user.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def player_info(request):
    """
    Returns a JSON representation of the logged in user.
    :param request: A get request from a logged in user.
    :return: A JSON representation of the logged in user.
    """

    try:
        # Get the logged in user
        user = request.user
        if user.is_anonymous:
            raise UserAnonymousException
        # Serialize the user
        if user.player is None:
            raise User
        serializer = serializers.PlayerSerializer(user.player)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserAnonymousException:
        return Response("Error: No user in request. Authorization token header may be missing or invalid.",
                        status=status.HTTP_400_BAD_REQUEST)
    except UserNotPlayerException:
        return Response("Error: The given user is not a player. Only player accounts can be used with this request.")



@api_view(['POST'])
def remove_balance(request):
    """
    Subtracts the specified amount from users balance. The user must be logged in through the token authentication
    system.dfsg
    :param request:Request containing the POST field 'amount' which is the amount to be subtracted to the users account.
    :return: A response containing a JSON representation of the user.
    """

    print(request)

    # Subtract the amount from the users balance
    request.user.balance = request.user.balance - Decimal(request.POST['amount'])
    # Save the changes to the user
    request.user.save()
    # Serialize the user
    serializer = serializers.UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_balance(request):
    """
    Adds the specified amount to the users balance. The user must be logged in through the token authentication
    system.
    :param request: Request containing the POST field 'amount' which is the amount to be added to the users account.
    :return: A response containing a JSON representation of the user.
    """
    # Adds the amount to the users balance
    request.user.balance = request.user.balance + Decimal(request.POST['amount'])
    # Saves the changes to the user
    request.user.save()
    # Serialize the user
    serializer = serializers.UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_game(request):
    """
    Returns a JSON representation of the game when given the game key.
    :param request: Request containing the Post field 'gameKey' containing the key of the game you wish to get a JSON
    representation of.
    :return: A JSON representation of the Game.
    """
    print(request)
    # Get the game from the game ID
    game = Game.objects.get(request.POST['gameId'])
    # Serizalize the game
    serializer = serializers.GameSerializer(game)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def start_match(request):
    """
    Creates a new match and returns the key.
    :param request: Request containing the Post fields 'gameKey' containing the key of the game you wish to create a
    match for and 'wager' containing the wager amount for the match.
    :return: A JSON representation of the key for the new match
    """

    # Get the game key and wager from the request.
    try:
        # Try to get the fields
        key = request.POST['gameKey']
        wager = request.POST['wager']

        # Get the game from the key
        game = Game.objects.get(key=key)

        # Create a new match
        wager = Decimal(wager)

        match = Match.objects.create(game=game, wager=wager)
        match.save()

        # Serialize the match
        serializer = serializers.MatchSerializerFull(match)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except MultiValueDictKeyError as e:
        # If any of the fields are missing return a 400 with an error message.
        if "gameKey" in str(e):
            return Response("Error: could not find field 'gameKey' in request.", status=status.HTTP_400_BAD_REQUEST)
        if "wager" in str(e):
            return Response("Error: could not find field 'wager' in request.", status=status.HTTP_400_BAD_REQUEST)
    except Game.DoesNotExist:
        # If a game matching key does not exist in the database.
        return Response("Error: Game matching the given gameKey does not exist in the database.",
                        status=status.HTTP_404_NOT_FOUND)
    except InvalidOperation:
        # If the user gave a non number for wager
        return Response("Error: Non-number value for wager.", status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_match(request):
    """
    Returns the match in JSON format. Including the match's UserGroups, which includes the users belonging to the
    user groups.
    :param request: The request, which should contain a Post field 'matchKey' containing the match's key
    :return: The match in JSON format.
    """

    try:
        # Get the match
        match = Match.objects.get(key=request.POST['matchKey'])
        # Serialize the match
        serializer = serializers.MatchSerializerFull(match)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except MultiValueDictKeyError as e:
        if "matchKey" in str(e):
            # If the field for matchKey is missing return a 400 error.
            return Response("Error: could not find field 'matchKey' in request.", status=status.HTTP_400_BAD_REQUEST)
    except Match.DoesNotExist:
        # If there is not a match that matches the matchKey return a 404 error.
        return Response("Error: Match matching the given matchKey does not exist in the database.",
                        status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def create_user_group(request):
    """
    Creates a new user group within the given match. Returns a JSON representation of the match. Should be given the
    game key and the match key. There must not be a user group with the same name that belongs to the match.
    :param request: Request containing a POST form with fields and values for 'gameKey', 'matchKey', and 'groupName'
    :return: JSON representation of the match if the operations was successful. Status 400 if unsuccessful.
    """
    try:
        # Get the game from the game key
        game = Game.objects.get(key=request.POST['gameKey'])
        # Get the match from the game and the match key
        match = Match.objects.get(game=game, key=request.POST['matchKey'])

        # If there isn't already a group of the given name in the match and the match has not ended
        if not match.usergroup_set.filter(name=request.POST['groupName']).exists() \
                and match.date_created == match.date_finished:
            # Create a new user group in the match with the given name
            PlayerGroup.objects.create(match=match, name=request.POST['groupName'])
            # Serialize the match
            serializer = serializers.MatchSerializerFull(match)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # If a usergroup with the given name already exists in the match...
            if match.usergroup_set.filter(name=request.POST['groupName']).exists():
                return Response("Error: A usergroup with the given groupName already exists in this match.",
                                status=status.HTTP_400_BAD_REQUEST)
            # If a the match has already finished...
            elif not match.date_created == match.date_finished:
                return Response("Error: The specified match has already ended.", status=status.HTTP_400_BAD_REQUEST)

    except MultiValueDictKeyError as e:
        # If any of the fields are missing return a 400 with an error message.
        if "gameKey" in str(e):
            return Response("Error: could not find field 'gameKey' in request.", status=status.HTTP_400_BAD_REQUEST)
        if "matchKey" in str(e):
            return Response("Error: could not find field 'matchKey' in request.", status=status.HTTP_400_BAD_REQUEST)
        if "groupName" in str(e):
            return Response("Error: could not find field 'groupName' in request.", status=status.HTTP_400_BAD_REQUEST)
    except Game.DoesNotExist:
        # If there is not a game that matches the gameKey return a 404 error.
        return Response("Error: Game matching the given gameKey does not exist in the database.",
                        status=status.HTTP_404_NOT_FOUND)
    except Match.DoesNotExist:
        # If there is not a match that matches the matchKey return a 404 error.
        return Response("Error: Match matching the given matchKey does not exist in the database.",
                        status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def add_user_to_group(request):
    """
    Adds the user to the specified user group. Returns a JSON representation of the match. Should be given game key,
    match key, group name, and the user key.
    :param request: Request containing a POST form with fields and values for 'gameKey, 'matchKey', 'groupName',
    and 'userKey'.
    :return: JSON representation of the match if operation was successful. If the operation was
    """
    try:
        # Get the game from the game key
        game = Game.objects.get(key=request.POST['gameKey'])
        # Get the match from the game and the match key
        match = Match.objects.get(game=game, key=request.POST['matchKey'])
        # Get the group from the match
        player_group = PlayerGroup.objects.get(match=match, name=request.POST['groupName'])
        # Get the user
        user = User.objects.get(auth_token=request.POST['auth_token'])

        # or should the users group just be changed?

        # If the user has enough in their balance and the match has not ended add them to the match
        if user.balance >= match.wager and match.date_created == match.date_finished and \
                user.user_group.match != match:
            # Set the users group to the specified user group
            user.user_group = player_group
            # The the wager amount from the user and add it to the pool
            user.balance = user.balance - match.wager
            match.pool = match.pool + Decimal(match.wager)
            user.save()
            match.save()

            # Save a user group user to make a record of the user and their group.
            player_group_user = PlayerGroupPlayer(player=user.player, player_group=player_group)
            player_group_user.save()

            # Serialize the match
            serializer = serializers.MatchSerializerFull(match)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # If the user does not have enough in their balance...
            if not user.balance >= match.wager:
                return Response("Error: Users balance is less than the wager.", status.HTTP_400_BAD_REQUEST)
            # If the match has already ended...
            elif not match.date_created == match.date_finished:
                return Response("Error: The specified match has already ended.", status.HTTP_400_BAD_REQUEST)
            elif user.user_group is not None:
                return Response("Error: The specified user is already in a user group.", status.HTTP_400_BAD_REQUEST)
    except MultiValueDictKeyError as e:
        # If any of the fields are missing return a 400 with an error message.
        if "gameKey" in str(e):
            return Response("Error: could not find field 'gameKey' in request.", status=status.HTTP_400_BAD_REQUEST)
        if "matchKey" in str(e):
            return Response("Error: could not find field 'matchKey' in request.",
                            status=status.HTTP_400_BAD_REQUEST)
        if "groupName" in str(e):
            return Response("Error: could not find field 'groupName' in request.",
                            status=status.HTTP_400_BAD_REQUEST)
        if "auth_token" in str(e):
            return Response("Error: could not find field 'auth_token' in request.",
                            status=status.HTTP_400_BAD_REQUEST)
    except Game.DoesNotExist:
        # If there is not a game that matches the gameKey return a 404 error.
        return Response("Error: Game matching the given gameKey does not exist in the database.",
                        status=status.HTTP_404_NOT_FOUND)
    except Match.DoesNotExist:
        # If there is not a match that matches the matchKey return a 404 error.
        return Response("Error: Match matching the given matchKey does not exist in the database.",
                        status=status.HTTP_404_NOT_FOUND)
    except PlayerGroup.DoesNotExist:
        # If there is not a UserGroup that matches the groupName return a 404 error.
        return Response("Error: UserGroup matching the given groupName does not exist in the database.",
                        status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        # If there is not a User that matches the auth_token return a 404 error.
        return Response("Error: User matching the given auth_token does not exist in the database.",
                        status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def payout(request):
    """
    Pays out the winning users in a match when given the group of winning users.
    :param request: A request containing the fields 'gameKey', 'matchKey' and 'groupName'. groupName is the name of the
    winning group
    :return: A json representation of the match
    """

    try:
        # Get the game from the game key
        game = Game.objects.get(key=request.POST['gameKey'])
        # Get the match from the game and the match key
        match = Match.objects.get(game=game, key=request.POST['matchKey'])
        # Get the group from the match
        player_group = PlayerGroup.objects.get(match=match, name=request.POST['groupName'])

        # If there is money in the pool and the match has not ended
        if match.pool > 0 and match.date_created == match.date_finished and player_group.user_set.count() > 0:
            # Get the payout amount by dividing the pool by the number of winners
            # pay_amount = match.pool / user_group.user_set.count()

            # The following lines are for handling remainders (You cant pay out less than a cent)

            # Times the pool times 100 and convert it to an int to perform integer division
            int_pool = int(match.pool * 100)
            # Get the pay amount in int form by performing integer division on the int pool
            int_pay_amount = int_pool // player_group.user_set.count()
            # Get the pay amount by converting to a float and dividing by 100
            pay_amount = (Decimal(int_pay_amount)) / 100
            # Get the int remainder by performing modulo on the int_pool
            int_remainder = int_pool % player_group.user_set.count()
            # Get the actual remainder by converting to a float and dividing by 100
            remainder = (Decimal(int_remainder)) / 100

            # Give the remainder to the first user in the group
            first_user = player_group.user_set.first()
            first_user.balance += remainder
            first_user.save()
            match.pool -= remainder

            # Divide the pool between the users
            for user in player_group.user_set.all():
                user.balance += pay_amount
                match.pool -= pay_amount
                user.save()

            match.save()
            serializer = serializers.MatchSerializerFull(match)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            if not match.pool > 0:
                return Response("Error: There is no money in the pool.(Pool == 0). Cannot payout.",
                                status=status.HTTP_400_BAD_REQUEST)
            elif not match.date_created == match.date_finished:
                return Response("Error: The match has already ended. Cannot Payout.",
                                status=status.HTTP_400_BAD_REQUEST)
            elif not player_group.user_set.count > 0:
                return Response("Error: There are no users in the specified group. Cannot Payout.",
                                status=status.HTTP_400_BAD_REQUEST)
    except MultiValueDictKeyError as e:
        # If any of the fields are missing return a 400 with an error message.
        if "gameKey" in str(e):
            return Response("Error: could not find field 'gameKey' in request.", status=status.HTTP_400_BAD_REQUEST)
        if "matchKey" in str(e):
            return Response("Error: could not find field 'matchKey' in request.",
                            status=status.HTTP_400_BAD_REQUEST)
        if "groupName" in str(e):
            return Response("Error: could not find field 'groupName' in request.",
                            status=status.HTTP_400_BAD_REQUEST)
    except Game.DoesNotExist:
        # If there is not a game that matches the gameKey return a 404 error.
        return Response("Error: Game matching the given gameKey does not exist in the database.",
                        status=status.HTTP_404_NOT_FOUND)
    except Match.DoesNotExist:
        # If there is not a match that matches the matchKey return a 404 error.
        return Response("Error: Match matching the given matchKey does not exist in the database.",
                        status=status.HTTP_404_NOT_FOUND)
    except PlayerGroup.DoesNotExist:
        # If there is not a UserGroup that matches the groupName return a 404 error.
        return Response("Error: UserGroup matching the given groupName does not exist in the database.",
                        status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def end_match(request):
    """
    Ends the given match. Which means there should be no more activity from the match
    :param request: A post request containing the fields 'gameKey' and 'matchKey' and their values. The match's pool
    should be equal to zero.
    :return: A JSON representation of the match
    """

    try:
        # Get the game from the game key
        game = Game.objects.get(key=request.POST['gameKey'])
        # Get the match from the game and the match key
        match = Match.objects.get(game=game, key=request.POST['matchKey'])

        # If there is no money left in the pool and the match has not already ended
        if match.pool == 0 and match.date_created == match.date_finished:
            match.date_finished = datetime.now()
            match.save()
            serializer = serializers.MatchSerializerFull(match)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif not match.pool == 0:
            return Response("Error: Cannot end match while there is still money in the pool.",
                            status=status.HTTP_400_BAD_REQUEST)
        elif not match.date_created == match.date_finished:
            return Response("Error: The match has already ended.", status=status.HTTP_400_BAD_REQUEST)
    except MultiValueDictKeyError as e:
        # If any of the fields are missing return a 400 with an error message.
        if "gameKey" in str(e):
            return Response("Error: could not find field 'gameKey' in request.", status=status.HTTP_400_BAD_REQUEST)
        if "matchKey" in str(e):
            return Response("Error: could not find field 'matchKey' in request.",
                            status=status.HTTP_400_BAD_REQUEST)
    except Game.DoesNotExist:
        # If there is not a game that matches the gameKey return a 404 error.
        return Response("Error: Game matching the given gameKey does not exist in the database.",
                        status=status.HTTP_404_NOT_FOUND)
    except Match.DoesNotExist:
        # If there is not a match that matches the matchKey return a 404 error.
        return Response("Error: Match matching the given matchKey does not exist in the database.",
                        status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def abort_match(request):
    """
    Aborts the match. All of the users have their money returned to them. This should be used for situations like when
    a dedicated server is disconnected.
    :param request: A post request containing the fields 'gameKey' and 'matchKey' and their values. The matches pool
    should not be equal to zero (payout should not have been called for the match)
    :return: A JSON representation of the match.
    """

    try:
        # Get the game from the game key
        game = Game.objects.get(key=request.POST['gameKey'])
        # Get the match from the game and the match key
        match = Match.objects.get(game=game, key=request.POST['matchKey'])

        # If there is money in the pool and the match has not ended
        if match.pool > 0 and match.date_created == match.date_finished:
            # Get the payout amount by dividing the pool by the number of winners
            # pay_amount = match.pool / user_group.user_set.count()

            # Divide the pool between all the users in the match
            for group in match.usergroup_set.all():
                for user in group.user_set.all():
                    user.balance += match.wager
                    match.pool -= match.wager
                    user.save()

            # End the match
            match.date_finished = datetime.now()
            match.save()
            serializer = serializers.MatchSerializerFull(match)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            if not match.pool > 0:
                return Response("Error: There is no money in the pool.(Pool == 0). Cannot payout.",
                                status=status.HTTP_400_BAD_REQUEST)
            elif not match.date_created == match.date_finished:
                return Response("Error: The match has already ended. Cannot Payout.",
                                status=status.HTTP_400_BAD_REQUEST)
    except MultiValueDictKeyError as e:
        # If any of the fields are missing return a 400 with an error message.
        if "gameKey" in str(e):
            return Response("Error: could not find field 'gameKey' in request.", status=status.HTTP_400_BAD_REQUEST)
        if "matchKey" in str(e):
            return Response("Error: could not find field 'matchKey' in request.",
                            status=status.HTTP_400_BAD_REQUEST)
    except Game.DoesNotExist:
        # If there is not a game that matches the gameKey return a 404 error.
        return Response("Error: Game matching the given gameKey does not exist in the database.",
                        status=status.HTTP_404_NOT_FOUND)
    except Match.DoesNotExist:
        # If there is not a match that matches the matchKey return a 404 error.
        return Response("Error: Match matching the given matchKey does not exist in the database.",
                        status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_400_BAD_REQUEST)
