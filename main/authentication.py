from rest_framework import authentication
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class BearerAuthentication(authentication.TokenAuthentication):
    '''
    Simple token based authentication using utvsapitoken.

    Clients should authenticate by passing the token key in the 'Authorization'
    HTTP header, prepended with the string 'Bearer '.  For example:

        Authorization: Bearer 956e252a-513c-48c5-92dd-bfddc364e812
    '''
    keyword = 'HTTP-AUTHORIZATION'

class EmailBackend(ModelBackend):
    def authenticate(self, username, password, **kwargs):
        print("Authenticating")
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username, password=password)
            return user
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None

def authenticate(username, password, **kwargs):
    print("Authenticating")
    UserModel = get_user_model()
    try:
        user = UserModel.objects.get(email=username, password=password)
        return user
    except UserModel.DoesNotExist:
        return None
    else:
        if user.check_password(password):
            return user
    return None