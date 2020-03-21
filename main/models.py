"""
Last edited by James Scarrow 2020-03-20
"""
import uuid
from datetime import datetime
# from djmoney.models.fields import MoneyField
from decimal import Decimal

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models, transaction
# ugetext_lazy is used for translating text to local language
# This should eventually be done manually
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from main.exceptions import *
from .managers import UserManager


# Database is in a prototype version right now and is mostly just being used to test outside functions such as player
# login, death etc. Should be reevaluated once all outside functions are working. Should consider keeping other games
# in mind when creating database do reduce future effort when more games are added.


# This is a model for the games. I'm not sure if it's more efficiant to keep a list of the usernames here or have
# The users be in game
# This model may be outdated, Should instead use serverplayer

class User(AbstractBaseUser, PermissionsMixin):
    """
    Represents a user. Contains their information and their balance. Their email is considered their username.
    """
    email = models.EmailField(_('Email Address'), unique=True, blank=False, null=False)
    user_name = models.CharField(_('Username'), max_length=30, blank=False, null=False, unique=True)

    date_joined = models.DateTimeField(_('Date Joined'), auto_now_add=True, blank=False, null=False)
    is_staff = models.BooleanField(_('Staff'), default=False)
    is_active = models.BooleanField(_('Active'), default=True)

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.email or not self.user_name or not self.password:
                raise TypeError
        super(User, self).save(*args, **kwargs)

    def get_full_name(self):
        # The user is identified by their email address
        return self.first_name + " " + self.last_name

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    if __name__ == '__main__':
        class Meta:
            verbose_name = _('User')
            verbose_name_plural = _('Users')


class Developer(models.Model):
    company_name = models.CharField(_('First Name'), max_length=30, blank=False, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, null=False, blank=False)

    def save(self, *args, **kwargs):
        if self.user is None or not self.company_name.strip():
            raise TypeError
        super(Developer, self).save(*args, **kwargs)


class Game(models.Model):
    """
    Represents the game. Should be created when the developer registers a new game. The key should be kept secret
    because it is used to start and access matches that belong to the game. Name is the name of the game. date_joined
    is the date the Game was created.
    """

    # The name of the game
    name = models.CharField(max_length=100, blank=False, null=False)
    key = models.CharField(max_length=100, blank=False, unique=True, default=uuid.uuid4)

    date_created = models.DateTimeField(_('Date Created'), auto_now_add=True)

    developer = models.ForeignKey(Developer, blank=False, unique=False, on_delete=models.CASCADE)

    approved = models.BooleanField(_('Approved'), blank=False, default=False)

    max_match_length = models.IntegerField(blank=False, null=False, default=1)

    # Game they don't need to create user groups every time they create a match.

    def save(self, *args, **kwargs):
        if not self.name or not self.name.strip():
            raise GameCreateError('Name cannot be empty.')

        if not self.pk:
            if self.date_created is not None:
                raise GameCreateError('Cannot set date created. This is done automatically.')
            if self.developer.game_set.filter(name=self.name).count() != 0:
                raise GameCreateError('User cannot create more than one game with the same name')
        super(Game, self).save(*args, **kwargs)

    def set_all_sandbox_players_balance(self, amount):
        for sandbox_player in self.sandboxplayer_set.all():
            sandbox_player.balance = amount
            sandbox_player.save()

    def delete_all_sandbox_players(self):
        self.sandboxplayer_set.all().delete()

    def update_sandbox_player(self, player_id, name, balance, password):
        sandbox_player = self.sandboxplayer_set.get(id=player_id)
        sandbox_player.name = name
        sandbox_player.balance = balance
        sandbox_player.password = password
        sandbox_player.save()

    def delete_sandbox_player(self, player_id):
        self.sandboxplayer_set.filter(id=player_id).delete()

    def create_sandbox_player(self, name, balance):
        self.sandboxplayer_set.create(name=name, balance=balance)

    def create_sandbox_players(self, prefix, count, balance):
        with transaction.atomic():
            starting_index = self.sandboxplayer_set.count()
            SandboxPlayer.objects.bulk_create([SandboxPlayer(name=prefix + str(x), game=self, balance=balance) for
                                               x in range(starting_index, starting_index+count)])

    def delete_all_sandbox_matches(self):
        self.sandboxplayer_set.all().delete()

    def create_sandbox_match_type(self, name):
        self.sandboxmatchtype_set.create(name=name)

    def delete_sandbox_match_type(self, match_type_id):
        self.sandboxmatchtype_set.filter(id=match_type_id).delete()

    def update_name(self, name):
        with transaction.atomic():
            self.name = name
            self.save()


class Match(models.Model):
    """
    A match in the game. Contains the amount of money currently in the pool. A unique key to access the match.
    Each match belongs to a game. Has a date created and date finished fields. The date_finished field should be
    set when the match is over. The date_finished is set to the same value as date_created when the Match is created,
    this is how you can tell the match is still going.
    """
    # The amount of money in the pool
    pool = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # The wager amount for the match
    wager = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # A unique identifier to be used to access the game
    key = models.CharField(max_length=100, blank=False, unique=False, default=uuid.uuid4)

    # The game the match belongs to
    game = models.ForeignKey(Game, blank=True, unique=False, on_delete=models.CASCADE)

    # Date the game started
    date_created = models.DateTimeField(_('Date Joined'), auto_now_add=True)
    # Date the game finished. Set to same as start date, should be set when the game is over
    date_finished = models.DateTimeField(_('Date Finished'), auto_now_add=True)


class PlayerGroup(models.Model):
    """
    Represents a UserGroup within a match. Contains a set of users. This can be used for assigning users
    to teams in a match. A UserGroup belongs to a match.
    """
    # The Match the UserGroup belongs to
    match = models.ForeignKey(Match, blank=False, on_delete=models.CASCADE)
    # Name of the UserGroup
    name = models.CharField(max_length=100, blank=True)


class Player(models.Model):

    # First and last name should be required in the future
    first_name = models.CharField(_('First Name'), max_length=30, blank=False)
    last_name = models.CharField(_('Last Name'), max_length=30, blank=False)

    in_game = models.BooleanField(_('In Game'), default=False)
    wager = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)


class PlayerGroupPlayer(models.Model):
    player = models.ForeignKey(Player, blank=False, on_delete=models.CASCADE)
    player_group = models.ForeignKey(PlayerGroup, blank=False, on_delete=models.CASCADE)

# ---------------------------------------------------- Sandbox ---------------------------------------------------------


class SandboxMatchType(models.Model):
    """
    Represents a type of match a sandbox game can have, e.g. Team Deathmatch, Free for all. It is not necessary for
    a match to have a match type but it can be useful for automatically setting up the match to have certain properties,
    such as groups that are created with the match (implementing) or preset payout schemes (idea).
    """
    name = models.CharField(max_length=50, blank=False, null=False)
    game = models.ForeignKey(Game, blank=False, null=False, on_delete=models.CASCADE)
    max_match_length = models.IntegerField(blank=False, null=False, default=60)

    def save(self, *args, **kwargs):

        if not self.name or not self.name.strip():
            raise MatchTypeCreationError("Error: Cannot create a match type without a name")
        if (not self.pk and self.game.sandboxmatchtype_set.filter(name=self.name).count() > 0) or  \
                (self.pk is not None and (self.name != SandboxMatchType.objects.get(id=self.pk).name)):
            raise MatchTypeCreationError("Error: Game already has a match type with the given name.")
        super(SandboxMatchType, self).save(*args, **kwargs)


class SandboxMatchTypeGroup(models.Model):
    """
    A preset group for a SandboxMatchType. When a match with a given match type is created player groups will
    automatically be created for each match type group belonging to the match type.
    """
    name = models.CharField(max_length=50, blank=False)
    match_type = models.ForeignKey(SandboxMatchType, blank=False, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.name or not self.name.strip():
            raise MatchTypeGroupCreationError("Error: Cannot create a match type group without a name")
        if self.match_type.sandboxmatchtypegroup_set.filter(name=self.name).count():
            raise MatchTypeGroupCreationError("Error: Match type already has a type group with the given name.")
        super(SandboxMatchTypeGroup, self).save(*args, **kwargs)


class SandboxMatch(models.Model):
    """
    A match in the game. Contains the amount of money currently in the pool. A unique key to access the match.
    Each match belongs to a game. Has a date created and date finished fields. The date_finished field should be
    set when the match is over. The date_finished is set to the same value as date_created when the Match is created,
    this is how you can tell the match is still going.
    """
    # The current amount of money in the pool
    pool = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # The maximum amount of money that has been in the pool
    maxPool = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # The wager in amount for the match
    wager = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # A unique identifier to be used to access the match
    key = models.CharField(max_length=100, blank=False, unique=False, default=uuid.uuid4)

    # The game the match belongs to
    game = models.ForeignKey(Game, blank=True, unique=False, on_delete=models.CASCADE)

    type = models.ForeignKey(SandboxMatchType, blank=True, null=True, unique=False, on_delete=models.SET_NULL)

    # The state of the match
    STATES = (
        (0, 'Registering'),
        (1, 'Active'),
        (2, 'Finished'),
        (3, 'Aborted'),
    )
    state = models.IntegerField(choices=STATES, default=0)

    # The winning group that has been payed out.
    winning_player_group = models.ForeignKey('SandboxPlayerGroup', blank=True, null=True, on_delete=models.CASCADE)

    # Date the game was created
    date_created = models.DateTimeField(_('Date Joined'), auto_now_add=True)

    # Date the game was started
    date_started = models.DateTimeField(_('Date Started'), blank=True, null=True)

    # Date the game finished. Set to same as start date, should be set when the game is over
    date_finished = models.DateTimeField(_('Date Finished'), blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.state != 0:
                raise MatchCreationError("Cannot set the state when creating a match, it is automatically"
                                         " set to registering.")
            if self.pool != 0:
                raise MatchCreationError("Cannot set the pool when creating a match.")
            if self.maxPool != 0:
                raise MatchCreationError("Cannot set the maxPool when creating a match.")
            if self.wager < 0:
                raise MatchCreationError("The wager for a match can not be less than zero.")
            super(SandboxMatch, self).save(*args, **kwargs)
            if self.type is not None:
                for type_group in self.type.sandboxmatchtypegroup_set.all():
                    self.create_player_group(type_group)
        else:
            super(SandboxMatch, self).save(*args, **kwargs)

    def start_match(self):
        if self.state == 1:
            raise MatchStartMatchError("Error: Cannot start the match, the match is in progress.")
        elif self.state == 2:
            raise MatchStartMatchError("Error: Cannot start the match, the match has already ended.")
        elif self.state == 3:
            raise MatchStartMatchError("Error: Cannot start the match, the match has been aborted.")
        elif self.sandboxplayergroup_set.count() < 2:
            raise MatchStartMatchError("Error: Cannot start the match, there must be at least 2 player groups.")
        elif self.pool == 0:
            raise MatchStartMatchError("Error: Cannot start the match, the pool must be greater than 0.")
        elif len(self.get_players()) < 2:
            raise MatchStartMatchError("Error: Cannot start the match, there must be at least 2 players")
        self.state = 1
        self.date_started = datetime.now()
        self.save()

    def create_player_group(self, sandbox_player_group_name_or_typegroup):

        # Check if the match is in the correct state
        if self.state == 0:

            # Check if there is a group with the same name
            group_with_name = self.sandboxplayergroup_set.filter(
                Q(name=sandbox_player_group_name_or_typegroup) |
                Q(type_group__name=sandbox_player_group_name_or_typegroup)).first()

            # If there isn't a group with the name create the group
            if group_with_name is None:

                if isinstance(sandbox_player_group_name_or_typegroup, str):
                    if sandbox_player_group_name_or_typegroup.strip() == "":
                        raise MatchCreateUserGroupError("Error: Usergroup cannot be empty or contain only whitespace.")
                    return SandboxPlayerGroup.objects.create(match=self, name=sandbox_player_group_name_or_typegroup)
                else:
                    return SandboxPlayerGroup.objects.create(match=self,
                                                             type_group=sandbox_player_group_name_or_typegroup)
            # Otherwise check if the group is removed
            elif group_with_name.removed:
                group_with_name.removed = False
                group_with_name.save()
                return group_with_name

        # If a user_group with the given name already exists in the match...
        if (self.sandboxplayergroup_set.filter(
                Q(name=sandbox_player_group_name_or_typegroup) |
                Q(type_group__name=sandbox_player_group_name_or_typegroup)).exists()):
            raise MatchCreateUserGroupError("Error: A usergroup with the given groupName already exists in"
                                            " this match.")
        # If a the match has already finished...
        elif self.state == 1:
            raise MatchCreateUserGroupError("Error: Cannot create a user group when the match has"
                                            " already started")
        elif self.state == 2:
            raise MatchCreateUserGroupError("Error: Cannot create a user group when the match has"
                                            " already ended")
        elif self.state == 3:
            raise MatchCreateUserGroupError("Error: Cannot create a user group when the match has"
                                            " already been aborted")

    def end_match(self, winning_player_group):
        # If there is money in the pool and the match has not ended
        if self.pool > 0 and self.state == 1 and \
                        winning_player_group.sandboxplayergroupplayer_set.count() > 0:

            # The following lines are for handling remainders (You cant pay out less than a cent)

            # Times the pool times 100 and convert it to an int to perform integer division
            int_pool = int(self.pool * 100)
            # Get the pay amount in int form by performing integer division on the int pool
            int_pay_amount = int_pool // winning_player_group.sandboxplayergroupplayer_set.count()
            # Get the pay amount by converting to a float and dividing by 100
            pay_amount = (Decimal(int_pay_amount)) / 100
            # Get the int remainder by performing modulo on the int_pool
            int_remainder = int_pool % winning_player_group.sandboxplayergroupplayer_set.count()
            # Get the actual remainder by converting to a float and dividing by 100
            remainder = (Decimal(int_remainder)) / 100

            # Give the remainder to the first user in the group
            first_player = winning_player_group.sandboxplayergroupplayer_set.first().player
            first_player.balance += remainder
            first_player.save()
            self.pool -= remainder

            # Divide the pool between the users
            for sandbox_player_group_player in winning_player_group.sandboxplayergroupplayer_set.all():
                sandbox_player = sandbox_player_group_player.player
                sandbox_player.balance += pay_amount
                self.pool -= pay_amount
                sandbox_player.save()

            self.date_finished = datetime.now()
            self.winning_player_group = winning_player_group
            self.state = 2
            self.save()

        else:
            if self.state == 0:
                raise MatchEndMatchError("Error: The match has not started yet.")
            elif self.state == 2:
                raise MatchEndMatchError("Error: The match has already ended.")
            elif self.state == 3:
                raise MatchEndMatchError("Error: The match has been aborted.")
            elif not self.pool > 0:
                raise MatchEndMatchError("Error: There is no money in the pool.(Pool == 0). Cannot payout.")
            elif not winning_player_group.sandboxplayergroupplayer_set.count() > 0:
                raise MatchEndMatchError("Error: There are no users in the specified group. Cannot Payout.")

    def __remove_player(self, sandbox_player_group_player):
        if sandbox_player_group_player.quit:
            raise RemovePlayerError("Error: Player has already quit.")
        if self.state == 2 or self.state == 3:
            raise RemovePlayerError("Error: The match is over")
        if self.pool <= 0:
            raise RemovePlayerError("Error: There is no money left in the pool")
        if sandbox_player_group_player.playerGroup.match != self:
            raise RemovePlayerError("Error: Player is not is this match")
        sandbox_player = sandbox_player_group_player.player
        sandbox_player.balance += self.wager
        self.pool -= self.wager
        self.maxPool -= self.wager
        sandbox_player.save()

    def abort_match(self):
        # If there is money in the pool and the match has not ended
        if self.state == 0 or self.state == 1:
            # Get the payout amount by dividing the pool by the number of winners
            # pay_amount = match.pool / user_group.user_set.count()

            if self.pool > 0:
                # Divide the pool between all the users in the match
                for group in self.sandboxplayergroup_set.all():

                    for sandbox_player_group_player in SandboxPlayerGroupPlayer.objects.filter(playerGroup=group,
                                                                                               quit=False):
                        self.__remove_player(sandbox_player_group_player)

            # End the match
            self.date_finished = datetime.now()
            self.state = 3
            self.save()
        else:
            if self.state == 2:
                raise MatchAbortMatchError("Error: The match has already ended. Cannot Abort.")
            elif self.state == 3:
                raise MatchAbortMatchError("Error: The match has already been aborted.")

    def player_quit(self, sandbox_player):
        if self.state == 1:
            raise PlayerQuitError("Error: Player cannot quit, the match is already in progress")
        elif self.state == 2:
            raise PlayerQuitError("Error: Player cannot quit, the match has already ended.")
        elif self.state == 3:
            raise PlayerQuitError("Error: Player cannot quit, the match has been aborted.")
        elif self.state != 0:
            raise PlayerQuitError("Error: Player cannot quit, the match is not in the registering state.")

        player_group = self.sandboxplayergroup_set.get(sandboxplayergroupplayer__player=sandbox_player)
        if player_group.match != self:
            raise PlayerQuitError("Error: Player is not in the match")
        sandbox_player_group_player = SandboxPlayerGroupPlayer.objects.select_for_update().get(player=sandbox_player,
                                                                                               playerGroup=player_group)
        if sandbox_player_group_player.quit:
            raise PlayerQuitError("Error: Player has already quit.")

        self.__remove_player(sandbox_player_group_player)
        self.save()
        # Set player quit to True
        sandbox_player_group_player.refresh_from_db()
        sandbox_player_group_player.quit = True
        sandbox_player_group_player.save()
        # If there are no players left in the player group, remove the player group.
        if player_group.getPlayerCount() == 0:
            self.remove_group(player_group)

    def remove_group(self, sandbox_player_group):
        if self.state != 0:
            raise RemoveGroupError("Cannot remove a group if the match is not in the registering state")
        if sandbox_player_group.match != self:
            raise RemoveGroupError("Group does not belong to this match.")
        if len(sandbox_player_group.getPlayers()) != 0:
            raise RemoveGroupError("Cannot remove a group that isn't empty.")
        if sandbox_player_group.removed:
            raise RemoveGroupError("The group has already been removed")

        sandbox_player_group.removed = True
        sandbox_player_group.save()

    def get_player_groups(self):
        groups = []
        for group in self.sandboxplayergroup_set.filter(removed=False):
            groups.append(group)
        return groups

    def get_players(self):
        players = []
        for group in self.sandboxplayergroup_set.all():
            players += group.getPlayers()
        print(len(players))
        return players

    def player_can_join(self, player):
        if SandboxPlayerGroupPlayer.objects.filter(playerGroup__match=self, player=player).count() != 0:
            sandbox_player_group_player = SandboxPlayerGroupPlayer.objects.get(playerGroup__match=self,
                                                                               player=player)
            if not sandbox_player_group_player.quit:
                raise PlayerGroupAddPlayerError("Error: The player has already joined the match.")
        # If the user does not have enough in their balance...
        if not player.balance >= self.wager:
            raise PlayerGroupAddPlayerError("Error: Users balance is less than the wager.")
        # If the match has already ended...
        elif not self.state == 0:
            raise PlayerGroupAddPlayerError("Error: The specified match has already ended.")
        # Check if the player is in a group and hasn't quit
        existing_playergroupplayer = SandboxPlayerGroupPlayer.objects.filter(playerGroup__match=self,
                                                                             player=player).first()
        if existing_playergroupplayer is not None and not existing_playergroupplayer.quit:
            raise PlayerGroupAddPlayerError("Error: The specified user is already in a user group.")

        return existing_playergroupplayer


class SandboxPlayerGroup(models.Model):
    """
    Represents a PlayerGroup within a match. Contains a set of players. This can be used for assigning players
    to teams in a match. A PlayerGroup belongs to a match.
    """

    # The Match the PlayerGroup belongs to
    match = models.ForeignKey(SandboxMatch, blank=False, on_delete=models.CASCADE)
    # Name of the PlayerGroup
    name = models.CharField(max_length=100, blank=True, null=True)

    type_group = models.ForeignKey(SandboxMatchTypeGroup, blank=True, null=True, on_delete=models.CASCADE)

    removed = models.BooleanField(blank=False, null=False, default=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            if(self.type_group is None and self.name is None) or \
                    (self.type_group is not None and self.name is not None):
                raise PlayerGroupCreationError("Error: PlayerGroup cannot have both a type_group and a name.")
        super(SandboxPlayerGroup, self).save(*args, **kwargs)

    def add_player(self, player):
        # If the player group has been removed a player cant be added to it
        if self.removed:
            raise PlayerGroupAddPlayerError("A player cannot be added to a player group that has been removed")

        existing_playergroupplayer = self.match.player_can_join(player)

        # The the wager amount from the user and add it to the pool
        player.balance = player.balance - self.match.wager
        self.match.pool = self.match.pool + Decimal(self.match.wager)
        self.match.maxPool = self.match.maxPool + Decimal(self.match.wager)

        player.save()
        self.save()
        self.match.save()

        if existing_playergroupplayer is None:
            # Save a user group user to make a record of the user and their group.
            SandboxPlayerGroupPlayer.objects.create(player=player, playerGroup=self)
        else:
            existing_playergroupplayer.quit = False
            existing_playergroupplayer.playerGroup = self
            existing_playergroupplayer.save()

    def getPlayers(self):
        """
        Gets all of the players that are currently in this player group. Players
        that were in this group and quit the match are not included in this list.
        :return: An array containing the sandbox players that are in this group.
        """
        players = []
        for pgp in self.sandboxplayergroupplayer_set.filter(quit=False):
            players.append(pgp.player)
        return players

    def getPlayerCount(self):
        """
        Gets the number of players that are currently in this player group. Players
        that were in this group and quit the match are not included in this count.
        :return: The number of players in this player group.
        """
        return self.sandboxplayergroupplayer_set.filter(quit=False).count()

    # This should be used when getting the name not the name property
    def get_name(self):
        if self.name is not None:
            return self.name
        else:
            return self.type_group.name


class SandboxPlayer(models.Model):
    """
    Sandbox players belong to a game. Developers can set their balance, name, password etc. and use the sandbox players
    with the sandbox API to test their matches. Sandbox players can join sandbox matches that belong to their game.
    Their balances will be updated when they join and finish matches just like a real players would.
    """
    name = models.CharField(_('Name'), max_length=30, blank=False, unique=False)
    date_created = models.DateTimeField(_('Date Created'), auto_now_add=True)
    game = models.ForeignKey(Game, blank=False, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    password = models.CharField(_('Password'), max_length=30, blank=False, unique=False, default="testpassword")

    def save(self, *args, **kwargs):
        if not self.name:
            raise PlayerCreateError("Error: Name cannot be None.")
        if not self.game:
            raise PlayerCreateError("Error: Sandbox player must have a game.")
        if Decimal(self.balance) < 0:
            raise PlayerCreateError("Error: Sandbox player can not have a balance less than 0.")
        if not self.pk:
            if SandboxPlayer.objects.filter(game=self.game, name=self.name).count() != 0:
                raise PlayerCreateError("Error: A sandbox player with the given name"
                                        " already exists for this game.")
        super(SandboxPlayer, self).save(*args, **kwargs)


class SandboxPlayerGroupPlayer(models.Model):
    """
    Represents the relationship between a sandbox player and a player group. Stores any information that has to do with
    that relationship.
    """
    player = models.ForeignKey(SandboxPlayer, blank=False, on_delete=models.CASCADE)
    playerGroup = models.ForeignKey(SandboxPlayerGroup, blank=False, on_delete=models.CASCADE)
    quit = models.BooleanField(blank=False, default=False)


# ---------------------------------------------------- FORUM -----------------------------------------------------------

class Category(models.Model):

    # Name of the category
    name = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return self.name


class Thread(models.Model):

    # Category
    category = models.ForeignKey(Category, blank=False, on_delete=models.CASCADE)
    # Title of the thread
    title = models.CharField(max_length=150, blank=False)
    # Number of times the thread has been viewed
    views = models.IntegerField(default=0, blank=False)
    # Is the thread pinned
    sticky = models.BooleanField(default=False, blank=False)

    def __str__(self):
        return self.title


class Message(models.Model):

    # User who posted the message
    user = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    # Thread the message belongs to
    thread = models.ForeignKey(Thread, blank=False, on_delete=models.CASCADE)
    # Text of the entry
    text = models.CharField(max_length=5000)
    # Date the post was made
    date = models.DateTimeField(_('Date Joined'), auto_now_add=True)

    def __str__(self):
        return self.user.user_name + " " + self.thread.title + " " + str(self.date)
