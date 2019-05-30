from django.contrib.auth import login
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect

from main import views
from main.exceptions import GameCreateError
from main.forms import UserLoginForm
from main.models import User, Game, Developer


def developers_home(request):
    return render(request, 'main/dev/index.html')


def reference(request):
    return render(request, 'main/dev/reference.html')


def reference_item(request, item):
    return render(request, 'main/dev/reference/' + item + ".html")


def signup(request):
    if request.user and not request.user.is_anonymous:
        if request.user.developer:
            return redirect(account)
        else:
            return redirect(views.account)
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            try:
                with transaction.atomic():
                    user = User.objects.create(email=request.POST['email'],  user_name=request.POST['user_name'],
                                               password=password)
                    Developer.objects.create(user=user, company_name=request.POST['company_name'])
                    login(request, user)
                    return redirect(account)
            except IntegrityError:
                return render(request, 'main/dev/signup.html', {'action': 'signup',
                                                            'errorMessage': 'A user with that email already exists.'})
        else:
            return render(request, 'main/dev/signup.html', {'action': 'signup',
                                                        'errorMessage': 'Error: Passwords did not match.'})
    if request.user and not request.user.is_anonymous and request.user.developer is not None:
        return redirect(account)
    return render(request, 'main/dev/signup.html', {'action': 'signup'})


def account(request):

    if request.user.is_authenticated:
        # If the user is a player redirect them to the player account page
        try:
            request.user.player
            return redirect('/account/')
        except:
            if request.method == 'POST':
                try:
                    Game.objects.create(name=request.POST['name'], developer=request.user.developer)
                except GameCreateError as e:
                    return render(request, 'main/dev/account.html', {'user': request.user,
                                                                      'errorMessage': 'Error: ' + str(e)})
            return render(request, 'main/dev/account.html', {'user': request.user})
    else:
        return render(request, 'main/login.html', {'form': UserLoginForm, 'action': 'sitelogin',
                                                   'errorMessage': 'Please login to view your account.'})


def change_company_name(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            dev = request.user.developer
            dev.company_name = request.POST['name']
            dev.save()
            return render(request, 'main/dev/account.html')
    return render(request, 'main/dev/account/changeComanyName.html')


def company_name(request):
    return render(request, 'main/dev/account/companyName.html')


def games(request):
    return render(request, 'main/dev/games.html')


def console_tutorial(request):
    return render(request, 'main/dev/tutorials/console.html')