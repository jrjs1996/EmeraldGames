from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status

from main.forms import UserLoginForm
from main.models import Game, SandboxMatchTypeGroup, SandboxMatchType


def sandbox(request, game):
    if request.user.is_authenticated:
        game = Game.objects.get(developer=request.user.developer, id=game)
        return render(request, 'main/dev/sandbox.html', {'game': game})
    else:
        return render(request, 'main/login.html', {'form': UserLoginForm, 'action': 'sitelogin',
                                                   'errorMessage': 'Please login to view your account.'})


def home(request, game):
    # Get the game
    g = Game.objects.get(id=game)

    registering_matches_count = g.sandboxmatch_set.filter(state=0).count()
    active_matches_count = g.sandboxmatch_set.filter(state=1).count()
    finished_matches_count = g.sandboxmatch_set.filter(state=2).count()
    aborted_matches_count = g.sandboxmatch_set.filter(state=3).count()

    # Make sure the user is authenticated and the game belongs to the user
    if request.user.is_authenticated and g.developer.user == request.user:
        return render(request, 'main/dev/sandbox/home.html', {'game': g,
                                                              'registering_matches_count': registering_matches_count,
                                                              'active_matches_count': active_matches_count,
                                                              'finished_matches_count': finished_matches_count,
                                                              'aborted_matches_count': aborted_matches_count})

    else:
        return render(request, 'main/login.html', {'form': UserLoginForm, 'action': 'sitelogin',
                                                   'errorMessage': 'Please login to view your account.'})


def players(request, game):
    # Get the game
    g = Game.objects.get(id=game)
    # Make sure the user is authenticated and the game belongs to the user
    if request.user.is_authenticated and g.developer.user == request.user:
        # Is the user updating the users?
        if request.method == "POST" :
            # Are they setting all balances
            if 'all' in request.POST:
                g.set_all_sandbox_players_balance(request.POST['amount'])
            # If the request contains id the user is trying to change a single user
            elif 'id' in request.POST:
                if 'delete' in request.POST:
                    g.delete_sandbox_player(request.POST['id'])
                else:
                    g.update_sandbox_player(request.POST['id'], request.POST['name'], request.POST['balance'],
                                            request.POST['password'])
            # If the user wants to create a player
            else:
                g.create_sandbox_player(name=request.POST['name'], balance=request.POST['balance'])

        players = g.sandboxplayer_set
        return render(request, 'main/dev/sandbox/players.html', {'players': players})

    return render(request, 'main/error.html', {'message': 'The page you are trying to access doesn\'t exist'})


def matches(request, game):
    g = Game.objects.get(id=game)
    # Make sure the user is authenticated and the game belongs to the user
    if request.user.is_authenticated and g.developer.user == request.user:
        matches = g.sandboxmatch_set
        return render(request, 'main/dev/sandbox/matches.html', {'matches': matches, 'game': g})

    return render(request, 'main/error.html', {'message': 'The page you are trying to access doesn\'t exist'})


def match(request, game, match):
    # Get the game
    g = Game.objects.get(id=game)
    # Make sure the user is authenticated and the game belongs to the user
    if request.user.is_authenticated and g.developer.user == request.user:
        # Get the match
        m = g.sandboxmatch_set.get(id=match)
        return render(request, 'main/dev/sandbox/match.html',{'match': m})

    return render(request, 'main/error.html', {'message': 'The page you are trying to access doesn\'t exist'})


def match_types(request, game):
    # Get the game
    g = Game.objects.get(id=game)
    # Make sure the user is authenticated and the game belongs to the user
    if request.user.is_authenticated and g.developer.user == request.user:
        match_types = g.sandboxmatchtype_set.all()
        # Get the matchTypes
        return render(request, 'main/dev/sandbox/matchTypes.html', {'game': g, 'matchTypes': match_types})


def match_type(request, game, match_type):
    # Get the game
    g = Game.objects.get(id=game)
    # Make sure the user is authenticated and the game belongs to the user
    if request.user.is_authenticated and g.developer.user == request.user:
        # Get the match type
        m_type = g.sandboxmatchtype_set.get(id=match_type)
        return render(request, 'main/dev/sandbox/matchType.html', {'matchType': m_type})


def settings(request, game):
    # Get the game
    g = Game.objects.get(id=game)

    # Make sure the user is authenticated and the game belongs to the user
    if request.user.is_authenticated and g.developer.user == request.user:
        if request.method == 'GET':
            return render(request, 'main/dev/sandbox/settings.html', {'game': g})
        if request.method == 'POST':
            with transaction.atomic():
                g = Game.objects.select_for_update().get(id=game)
                if request.POST['operation'] == 'changeName':
                    g.update_name(request.POST['name'])

                elif request.POST['operation'] == 'generatePlayers':
                    g.create_sandbox_players(request.POST['prefix'],
                                             int(request.POST['num']),
                                             float(request.POST['balance']))

                elif request.POST['operation'] == 'deleteAllPlayers':
                    g.delete_all_sandbox_players()

                elif request.POST['operation'] == 'deleteAllMatches':
                    g.delete_all_sandbox_matches()

                elif request.POST['operation'] == 'addMatchType':
                    g.create_sandbox_match_type(request.POST['name'])

                elif request.POST['operation'] == 'deleteMatchType':
                    g.delete_sandbox_match_type(request.POST['id'])

                elif request.POST['operation'] == 'addGroupPreset':
                    SandboxMatchTypeGroup.objects.create(name=request.POST['name'], match_type_id=request.POST['matchType'])

                elif request.POST['operation'] == 'deleteGroupPreset':
                    SandboxMatchTypeGroup.objects.filter(id=request.POST['id']).delete()

                elif request.POST['operation'] == 'deleteGame':
                    g.delete()

                elif request.POST['operation'] == 'changeDefaultMaxMatchLength':
                    defaultMatchLength = int(request.POST['defaultMaxMatchLength'])
                    g.max_match_length = defaultMatchLength
                    g.save()

                else:
                    return HttpResponse('Invalid Operation')

                return HttpResponse('Success')

    return render(request, 'main/error.html', {'message': 'The page you are trying to access doesn\'t exist'})


def change_max_match_length(request):
    if request.method == "POST" and request.user.is_authenticated:
        try:
            match_type = SandboxMatchType.objects.get(id=int(request.POST['matchTypeId']))
            if match_type.game.developer == request.user.developer:
                match_type.max_match_length = request.POST['maxMatchLength']
                match_type.save()
                return render(request, 'main/dev/sandbox/matchType/maxMatchLength.html', {'matchType': match_type})
        except ValueError:
            return HttpResponse("Value not valid for max match length. Please enter an integer.",
                                status=status.HTTP_400_BAD_REQUEST, )

    return render(request, 'main/dev/sandbox/matchType/changeMaxMatchLength.html')


def max_match_length(request):
    return render(request, 'main/dev/sandbox/matchType/maxMatchLength.html')
