from django.test import TestCase

from main.exceptions import *
from main.models import User, Developer, Game, SandboxMatchType, SandboxMatchTypeGroup, SandboxMatch, \
    SandboxPlayerGroup, SandboxPlayer


class CreateUserTestCase(TestCase):
    """
        email A Should not be blank or null
        user_name B Should not be blank or null
                  C Should not have multiple users with same user_name
        date_joined D Should not be blank or null
                    E Should not be able to be set when being created ( Set by auto_now_add)
        is_staff F Should default to false
        is_active G Should default to true
        balance H Should default to 0
                I Should not be able to set when being created
        """
    def setUp(self):
        User.objects.create(email='test@email.com', user_name='test_user', password='test_password')

    def test_user_creation(self):
        user = User.objects.get(email='test@email.com')
        self.assertEqual(user.email, 'test@email.com')
        self.assertEqual(user.user_name, 'test_user')
        self.assertEqual(user.password, 'test_password')
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.balance, 0)

    def test_missing_email(self):
        self.assertRaises(TypeError, User.objects.create, user_name='test_user2', password='test_password')

    def test_missing_username(self):
        self.assertRaises(TypeError, User.objects.create, email='test2@email.com', password='test_password')

    def test_missing_password(self):
        self.assertRaises(TypeError, User.objects.create, email='test3@email.com', user_name='test_user3')

    def test_duplicate_email(self):
        self.assertRaises(Exception, User.objects.create, email='test@email.com', user_name='test_user',
                          password='test_password')


class CreateSandboxPlayerGroupTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(email='test@email.com', user_name='test_user', password='test_password')
        developer = Developer.objects.create(user=user, company_name='test_company')
        game = Game.objects.create(developer=developer, name='test_game')
        sandbox_match_type = SandboxMatchType.objects.create(game=game, name="test_match_type")
        sandbox_match_type_group = SandboxMatchTypeGroup.objects.create(match_type=sandbox_match_type,
                                                                        name="test_match_type_group")
        sandbox_match = SandboxMatch.objects.create(game=game, type=sandbox_match_type, wager=1, key='1')
        SandboxPlayerGroup.objects.create(match=sandbox_match, type_group= sandbox_match_type_group)
        SandboxPlayerGroup.objects.create(match=sandbox_match, name="sandbox_player_group")

    def test_sandbox_player_group_creation_with_match_type(self):
        sandbox_match = SandboxMatch.objects.get(key='1')
        sandbox_match_type_group = SandboxMatchTypeGroup.objects.get(name="test_match_type_group")
        sandbox_player_group = SandboxPlayerGroup.objects.filter(type_group= sandbox_match_type_group)[1]
        self.assertEqual(sandbox_player_group.match, sandbox_match)
        self.assertEqual(sandbox_player_group.type_group, sandbox_match_type_group)
        self.assertIsNone(sandbox_player_group.name)

    def test_sandbox_player_group_creation_with_name(self):
        sandbox_match = SandboxMatch.objects.get(key='1')
        sandbox_player_group = SandboxPlayerGroup.objects.get(name="sandbox_player_group")
        self.assertEqual(sandbox_player_group.match, sandbox_match)
        self.assertEqual(sandbox_player_group.name, 'sandbox_player_group')
        self.assertIsNone(sandbox_player_group.type_group)

    def test_sandbox_player_group_creation_with_name_and_type_group(self):
        sandbox_match_type_group = SandboxMatchTypeGroup.objects.get(name="test_match_type_group")
        self.assertRaises(PlayerGroupCreationError, SandboxPlayerGroup.objects.create,
                          name="sandbox_player_group", type_group=sandbox_match_type_group)

    def test_sandbox_player_group_creation_with_no_name_and_no_type_group(self):
        self.assertRaises(PlayerGroupCreationError, SandboxPlayerGroup.objects.create)


class SandboxPlayerCreationTestCase(TestCase):
    """
    name A Should not be blank or null (required).
         B A game should not be able to have multiple sandbox players with the same name.
         C Sandbox players can have the same name if they do not belong to the same game.
    player_group D Should initialise to null
                 E Should not be able to be set outside the model when creating
    date_created F Should not be blank or null
    game G Should be required
    balance H Default should be 0
    password I Should have a default value

    """
    def setUp(self):
        user = User.objects.create(email='test@email.com', user_name='test_user', password='test_password')
        developer = Developer.objects.create(user=user, company_name='test_company')
        game = Game.objects.create(developer=developer, name='test_game')
        sandbox_match = SandboxMatch.objects.create(game=game, wager=1, key='1')
        SandboxPlayerGroup.objects.create(match=sandbox_match, name="sandbox_player_group")
        SandboxPlayer.objects.create(game=game, name='test_player', password='test_password')
        SandboxPlayer.objects.create(game=game, name='test_player_2')
        Game.objects.create(developer=developer, name='test_game_2')

    def test_sandbox_player_creation(self):
        game = Game.objects.get(name='test_game')
        sandbox_player = SandboxPlayer.objects.get(name='test_player')
        self.assertEqual(sandbox_player.name, 'test_player')
        self.assertEqual(sandbox_player.game, game)
        self.assertEqual(sandbox_player.balance, 0)
        self.assertEqual(sandbox_player.password, 'test_password')

    def test_A(self):
        game = Game.objects.get(name='test_game')
        self.assertRaises(PlayerCreateError, SandboxPlayer.objects.create, game=game, password='test_password')

    def test_B(self):
        game = Game.objects.get(name='test_game')
        self.assertRaises(PlayerCreateError, SandboxPlayer.objects.create, game=game, name='test_player',
                          password='test_password')

    def test_C(self):
        game = Game.objects.get(name='test_game_2')
        SandboxPlayer.objects.create(game=game, name='test_player', password='test_password')

    def test_D(self):
        sandbox_player = SandboxPlayer.objects.get(name='test_player')
        self.assertIsNone(sandbox_player.player_group)

    def test_E(self):
        game = Game.objects.get(name='test_game')
        player_group = SandboxPlayerGroup.objects.get(name='sandbox_player_group')
        self.assertRaises(PlayerCreateError, SandboxPlayer.objects.create, game=game, name='test_player_3',
                          player_group=player_group)

    def test_F(self):
        sandbox_player = SandboxPlayer.objects.get(name='test_player')
        self.assertIsNotNone(sandbox_player.date_created)

    def test_G(self):
        self.assertRaises(SandboxPlayer.game.RelatedObjectDoesNotExist, SandboxPlayer.objects.create,
                          name='test_player_3', password='test_password')

    def test_H(self):
        sandbox_player = SandboxPlayer.objects.get(name='test_player')
        self.assertEqual(sandbox_player.balance, 0)

    def test_I(self):
        sandbox_player = SandboxPlayer.objects.get(name='test_player_2')
        self.assertIsNotNone(sandbox_player.password)
