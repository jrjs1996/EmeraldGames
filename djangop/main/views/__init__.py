import json

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from rest_framework import status
from rest_framework.response import Response

import main.views.dev
from main.authentication import authenticate
from main.forms import UserLoginForm
from main.models import User, Player


# from rest_framework.authtoken.models import Token


def chat(request):
    return render(request, 'main/chat.html', {})


def room(request, room_name):
    return render(request, 'main/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })


def index(request):
    # cl = get_channel_layer()
    # async_to_sync(cl.send)('Hello', {'type': 'chat_message', 'message': "Hello world!"})
    return render(request, 'main/index.html')


def how_to_play(request):
    return render(request, 'main/howToPlay.html')


def site_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)

            # This is all for the login testing, it should be changed later
            # Add the user to the server
            return redirect(account)
        else:
            return render(request, 'main/login.html', {'form': UserLoginForm, 'action': 'sitelogin',
                                                       'errorMessage': 'Invalid Login. Please check your username'
                                                                       ' and password or create an account.'})
    return render(request, 'main/login.html', {'form': UserLoginForm, 'action': 'sitelogin'})


def site_logout(request):
    logout(request)
    return render(request, 'main/login.html', {'form': UserLoginForm, 'action': 'sitelogin',
                                               'errorMessage': 'You have been logged out.'})


def signup(request):
    if request.user and not request.user.is_anonymous:
        if request.user.developer:
            return redirect(dev.account)
        else:
            return redirect(account)

    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            try:
                    # Create the user for the player
                    user = User.objects.create(email=request.POST['email'],  user_name=request.POST['user_name'],
                                               password=password)
                    user.save()
                    try:
                        player = Player.objects.create(user=user, first_name=request.POST['first_name'],
                                                       last_name=request.POST['last_name'])
                        player.save()
                    except Exception as e:
                        user.delete()

                    login(request, user)
                    return redirect(account)
            except IntegrityError:
                return render(request, 'main/signup.html', {'action': 'signup',
                                                            'errorMessage': 'A user with that email already exists.'})
        else:
            return render(request, 'main/signup.html', {'action': 'signup',
                                                        'errorMessage': 'Error: Passwords did not match.'})

    return render(request, 'main/signup.html', {'action': 'signup'})


def account(request):
    if request.user.is_authenticated:
        # If the user is a developer redirect them to developer account
        try:
            request.user.developer
            return redirect('/dev/account')
        except:
            return render(request, 'main/account.html', {'user': request.user})
    else:
        return render(request, 'main/login.html', {'form': UserLoginForm, 'action': 'sitelogin',
                                                   'errorMessage': 'Please login to view your account.'})


def deposit(request):
    # If the user is logged in...
    if request.user.is_authenticated:
        # If the user is going to the deposit page from a server login screen send the server ID to the page so the page
        # can display a button that takes them back to the server login screen.
        if 's' in request.GET:
            server_id = request.GET['s']
            return render(request, 'main/deposit.html', {'serverId': server_id})
        return render(request, 'main/deposit.html')
    return Response(status=status.HTTP_400_BAD_REQUEST)


def deposit_made(request):
    amount = int(request.POST['amount'])
    if request.user.is_authenticated and amount > 0:
        request.user.balance += amount
        request.user.save()
        # If the user is going to the deposit page from a server login screen send the server ID to the page so the page
        # can display a button that takes them back to the server login screen.
        if 's' in request.GET:
            server_id = request.GET['s']
            return render(request, 'main/depositMade.html', {'serverId': server_id})

        return render(request, 'main/depositMade.html', {'amount': amount})

    return Response(status=status.HTTP_400_BAD_REQUEST)


def forum_activity(request):
    return render(request, 'main/forumactivity.html')