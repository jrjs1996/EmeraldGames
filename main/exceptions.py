class PlayerInvalidLogin(Exception):
    def __init__(self):
        super().__init__("Player with the given username and password not found.")
        self.code = 1


class PlayerInvalidAuthToken(Exception):
    def __init__(self):
        super().__init__("The given auth token is invalid.")
        self.code = 2


class MatchCreationError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.code = 3


class InvalidGameKey(Exception):
    def __init__(self):
        # Call the base class constructor with the parameters it needs
        super().__init__("Game matching the given gameKey does not exist in the database.")
        self.code = 4


class InvalidMatchType(Exception):
    def __init__(self):
        # Call the base class constructor with the parameters it needs
        super().__init__("Match type with the given name does not exist in the database.")
        self.code = 5


class MissingFieldError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.code = 6


class MatchStartMatchError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.code = 7


class MatchCreateUserGroupError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.code = 8


class GameNotFound(Exception):
    def __init__(self):
        # Call the base class constructor with the parameters it needs
        super().__init__("Game could not be found. Make sure the game key is correct.")
        self.code = 9


class MatchNotFound(Exception):
    def __init__(self):
        # Call the base class constructor with the parameters it needs
        super().__init__("Match could not be found. Make sure the game and match keys are correct.")
        self.code = 10


class PlayerGroupNotFound(Exception):
    def __init__(self):
        # Call the base class constructor with the parameters it needs
        super().__init__("PlayerGroup could not be found. Make sure the game key, match key,"
                         "and group name are correct.")
        self.code = 11


class PlayerNotFound(Exception):
    def __init__(self):
        # Call the base class constructor with the parameters it needs
        super().__init__("Player could not be found. Make sure the players auth token is correct.")
        self.code = 12

class MatchEndMatchError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.code = 13

class MatchAbortMatchError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.code = 14

class PlayerGroupAddPlayerError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.code = 15

class PlayerQuitError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.code = 16

class PlayerCreateError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.code = 17


class GameCreateError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.code = 18

class UserAnonymousException(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.code = 19


class UserNotPlayerException(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.code = 20


class PlayerGroupCreationError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.code = 21


class MatchTypeCreationError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.code = 22


class MatchTypeGroupCreationError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.code = 23


class RemoveGroupError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.code = 24


class ActionMissingError(Exception):
    def __init__(self):
        # Call the base class constructor with the parameters it needs
        super().__init__("Could not find the action in the message.")
        self.code = 25


class InvalidDataError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.code = 26


class InvalidJoinKeyError(Exception):
    def __init__(self):
        # Call the base class constructor with the parameters it needs
        super().__init__("Invalid join key provided. There is no player that matches this join key.")
        self.code = 27


class PlayerInMatchError(Exception):
    def __init__(self):
        # Call the base class constructor with the parameters it needs
        super().__init__("Error: player is already in a match. Player cannot be in more than one match at a time.")
        self.code = 28


class RemovePlayerError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.code = 29


class ActionNotFoundError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.code = 30


class PlayerInGameError(Exception):
    def __init__(self):
        # Call the base class constructor with the parameters it needs
        super().__init__("This player is in game. Only one connection is allowed per player.")
        self.code = 31


def serialize_exception(exception):
    return {'Code': exception.code, 'Message': str(exception)}
