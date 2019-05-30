from django.test import TestCase

from main.exceptions import *
from main.models import User, Developer, Game, SandboxMatchType


class CreateSandboxMatchTypeTestCase(TestCase):
    """
    name A Should not be null
         B Should not be empty
         C Game should not have more than one match type with the same name.
         D Match types can have the same name if the don't belong to the same game.
    game E Should not be null or empty
    """
    def setUp(self):
        user = User.objects.create(email='test@email.com', user_name='test_user', password='test_password')
        developer = Developer.objects.create(user=user, company_name='test_company')
        game = Game.objects.create(developer=developer, name='test_game')
        SandboxMatchType.objects.create(game=game, name="test_match_type")
        Game.objects.create(developer=developer, name='test_game_2')

    def test_sandbox_match_type_creation(self):
        game = Game.objects.get(name='test_game')
        match_type = SandboxMatchType.objects.get(name='test_match_type')
        self.assertEqual(match_type.name, 'test_match_type')
        self.assertEqual(match_type.game, game)

    def test_A(self):
        game = Game.objects.get(name='test_game')
        self.assertRaises(MatchTypeCreationError, SandboxMatchType.objects.create, game=game)

    def test_B(self):
        game = Game.objects.get(name='test_game')
        self.assertRaises(MatchTypeCreationError, SandboxMatchType.objects.create, game=game,
                          name=' ')

    def test_C(self):
        self.assertRaises(SandboxMatchType.game.RelatedObjectDoesNotExist, SandboxMatchType.objects.create,
                          name='test_match_type_2')

    def test_D(self):
        game = Game.objects.get(name='test_game_2')
        SandboxMatchType.objects.create(game=game, name="test_match_type")

    def test_E(self):
        game = Game.objects.get(name='test_game')
        self.assertRaises(MatchTypeCreationError, SandboxMatchType.objects.create, game=game,
                          name="test_match_type")


class DeleteGameTestCase(TestCase):
    """
    Tests the effect of a matches game being deleted on the match type.
    A - The match type should be deleted when the game is deleted.
    """
    def setUp(self):
        user = User.objects.create(email='test@email.com', user_name='test_user', password='test_password')
        developer = Developer.objects.create(user=user, company_name='test_company')
        game = Game.objects.create(developer=developer, name='test_game')
        SandboxMatchType.objects.create(game=game, name="test_match_type")

    def test_A(self):
        game = Game.objects.get(name='test_game')
        game.delete()
        self.assertEqual(SandboxMatchType.objects.all().count(), 0)
