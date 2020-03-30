from datetime import datetime
from decimal import InvalidOperation

from django.http import JsonResponse
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import status

from main.exceptions import *
from main.models import Game, SandboxMatchType, SandboxMatch, SandboxPlayerGroup
from main.models import SandboxPlayer


class SandboxMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.

        if request.path[:9] == "/sandbox/":
            response['ServerTime'] = str(datetime.now())
        return response

    def process_exception(self, request, exception):
        if request.path[:9] == "/sandbox/":
            path = request.path[9:]
            return self.handle_sandbox_exceptions(path, exception)
        return

    def handle_sandbox_exceptions(self, path, exception):
        response_status = status.HTTP_400_BAD_REQUEST
        if hasattr(exception, "code"):
            return JsonResponse(serialize_exception(exception), status=response_status)
        elif type(exception) == MultiValueDictKeyError:
            response_status = status.HTTP_400_BAD_REQUEST
        elif path == "playerinfo/" and \
                (type(exception) == SandboxPlayer.DoesNotExist or type(exception) == ValueError):
            response_status = status.HTTP_404_NOT_FOUND
        elif path == "creatematch/" and \
                (type(exception) == Game.DoesNotExist or type(exception) == SandboxMatchType.DoesNotExist):
            response_status = status.HTTP_404_NOT_FOUND
        else:
            response_status = status.HTTP_404_NOT_FOUND

        exception = SandboxMiddleware.get_sandbox_exception(exception, path[:-1])

        return JsonResponse(serialize_exception(exception), status=response_status)

    @staticmethod
    def get_sandbox_exception(exception, action):
        if hasattr(exception, "code"):
            return exception
        elif type(exception) == MultiValueDictKeyError:
            return SandboxMiddleware.handle_MultiValueDictKeyError(exception)
        elif action == "authtoken":
            return SandboxMiddleware.handle_auth_token_exceptions(exception)
        elif action == "playerinfo":
            return SandboxMiddleware.handle_player_info_exceptions(exception)
        elif action == "creatematch":
            return SandboxMiddleware.handle_sandbox_create_match_exceptions(exception)
        else:
            result = SandboxMiddleware.handle_does_not_exist_exceptions(exception)
            if result is not None:
                return result
            if action == "":
                return ActionMissingError()

    @staticmethod
    def handle_does_not_exist_exceptions(exception):
        if type(exception) == Game.DoesNotExist:
            return GameNotFound()
        elif type(exception) == SandboxMatch.DoesNotExist:
            return MatchNotFound()
        elif type(exception) == SandboxPlayerGroup.DoesNotExist:
            return PlayerGroupNotFound()
        elif type(exception) == SandboxPlayer.DoesNotExist:
            return PlayerNotFound()

    @staticmethod
    def handle_auth_token_exceptions(exception):
        if type(exception) == SandboxPlayer.DoesNotExist:
            exception = PlayerInvalidLogin()
        return exception

    @staticmethod
    def handle_player_info_exceptions(exception):
        if type(exception) == SandboxPlayer.DoesNotExist or type(exception) == ValueError:
            exception = PlayerInvalidAuthToken()
        return exception

    @staticmethod
    def handle_sandbox_create_match_exceptions(exception):
        if type(exception) == Game.DoesNotExist:
            exception = InvalidGameKey()
        elif type(exception) == SandboxMatchType.DoesNotExist:
            exception = InvalidMatchType()
        elif type(exception) == InvalidOperation:
            exception = MatchCreationError("Non-number value for wager")
        elif type(exception) == TypeError:
            exception = InvalidDataError("The data provided was invalid. Data for the creatematch action must be a"
                                         "JSON object with a wager_amount and optionally a match_type")

        return exception

    @staticmethod
    def handle_MultiValueDictKeyError(e):
        # If any of the fields are missing return a 400 with an error message.
        if "gameKey" in str(e):
            e = MissingFieldError("Could not find field 'gameKey' in request.")
        elif "matchKey" in str(e):
            e = MissingFieldError("Could not find field 'matchKey' in request.")
        elif "groupName" in str(e):
            e = MissingFieldError("Could not find field 'groupName' in request.")
        elif "auth_token" in str(e):
            e = MissingFieldError("Could not find field 'auth_token' in request.")
        elif "wager" in str(e):
            e = MissingFieldError("Could not find field 'wager' in request.")
        elif "username" in str(e):
            e = MissingFieldError("Could not find field 'username' in request.")

        return e
