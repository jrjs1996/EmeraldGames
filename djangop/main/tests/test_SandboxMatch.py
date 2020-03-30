from django.db.utils import IntegrityError
from django.test import TestCase

from main.exceptions import *
from main.models import User, Developer, Game, SandboxMatchType, SandboxMatchTypeGroup, SandboxMatch


class CreateSandboxMatchTestCase(TestCase):
    """
    pool A Should default to 0
         B Should not be able to be set when creating the SandboxMatch
    maxPool C Should default to 0
            D Should not be able to be set when creating the SandboxMatch
    wager E Cant be less than 0
          F Default should be 0
    key G Should not be Null or Blank (Created automatically)
    game H Should not be Null or Blank, must be set
    type I Should be able to set at creation
         J Should be null if no type is given at creation
    state K Should default to 0
          L Should net be able to set when creating the SandboxMatch
    winning_player_group M Default should be Null
    """
    def setUp(self):
        user = User.objects.create(email='test@email.com', user_name='test_user', password='test_password')
        developer = Developer.objects.create(user=user, company_name='test_company')
        game = Game.objects.create(developer=developer, name='test_game')
        sandbox_match_type = SandboxMatchType.objects.create(game=game, name="test_match_type")
        SandboxMatchTypeGroup.objects.create(match_type=sandbox_match_type,
                                             name="test_match_type_group")
        SandboxMatch.objects.create(game=game, type=sandbox_match_type, wager=1, key='1')
        SandboxMatch.objects.create(game=game, wager=1, key='2')
        SandboxMatch.objects.create(game=game, key='3')

    def check_defaults(self, sandbox_match):
        self.assertEqual(sandbox_match.pool, 0)
        self.assertEqual(sandbox_match.maxPool, 0)
        self.assertEqual(sandbox_match.state, 0)
        self.assertIsNone(sandbox_match.winning_player_group)
        self.assertIsNone(sandbox_match.date_started)
        self.assertIsNone(sandbox_match.date_finished)

    def test_A(self):
        sandbox_match = SandboxMatch.objects.get(key='1')
        self.assertEqual(sandbox_match.pool, 0)

    def test_B(self):
        game = Game.objects.get(name='test_game')
        self.assertRaises(MatchCreationError, SandboxMatch.objects.create, game=game, wager=1, pool=4)

    def test_C(self):
        sandbox_match = SandboxMatch.objects.get(key='1')
        self.assertEqual(sandbox_match.maxPool, 0)

    def test_D(self):
        game = Game.objects.get(name='test_game')
        self.assertRaises(MatchCreationError, SandboxMatch.objects.create, game=game, wager=1, maxPool=4)

    def test_E(self):
        game = Game.objects.get(name='test_game')
        self.assertRaises(MatchCreationError, SandboxMatch.objects.create, game=game, wager=-1)

    def test_F(self):
        game = Game.objects.get(name='test_game')
        sandbox_match = SandboxMatch.objects.get(key='3')
        self.check_defaults(sandbox_match)
        self.assertEqual(sandbox_match.wager, 0)
        self.assertEqual(sandbox_match.game, game)

    def test_G(self):
        sandbox_match = SandboxMatch.objects.get(key='1')
        self.assertIsNotNone(sandbox_match.key)

    def test_H(self):
        game = Game.objects.get(name='test_game')
        self.assertRaises(IntegrityError, SandboxMatch.objects.create, wager=1)

    def test_I(self):
        sandbox_match_type = SandboxMatchType.objects.get(name="test_match_type")
        sandbox_match_type_group = SandboxMatchTypeGroup.objects.get(name="test_match_type_group")
        game = Game.objects.get(name='test_game')
        sandbox_match = SandboxMatch.objects.get(key='1')
        self.check_defaults(sandbox_match)
        self.assertEqual(sandbox_match.wager, 1)
        self.assertEqual(sandbox_match.game, game)
        self.assertEqual(sandbox_match.type, sandbox_match_type)
        self.assertEqual(sandbox_match.sandboxplayergroup_set.count(), 1)
        self.assertEqual(sandbox_match.sandboxplayergroup_set.first().type_group, sandbox_match_type_group)

    def test_J(self):
        game = Game.objects.get(name='test_game')
        sandbox_match = SandboxMatch.objects.get(key='2')
        self.check_defaults(sandbox_match)
        self.assertEqual(sandbox_match.wager, 1)
        self.assertEqual(sandbox_match.game, game)
        self.assertIsNone(sandbox_match.type)

    def test_K(self):
        sandbox_match = SandboxMatch.objects.get(key='1')
        self.assertEqual(sandbox_match.state, 0)

    def test_L(self):
        game = Game.objects.get(name='test_game')
        self.assertRaises(MatchCreationError, SandboxMatch.objects.create, game=game, wager=1, state=3)

    def test_M(self):
        sandbox_match = SandboxMatch.objects.get(key='1')
        self.assertIsNone(sandbox_match.winning_player_group)


class DeleteGameTestCase(TestCase):
    """
    Tests the effect of a SandboxMatches Game being deleted on the SandboxMatch.
    A - The match should be deleted when the game is deleted
    """
    def setUp(self):
        user = User.objects.create(email='test@email.com', user_name='test_user', password='test_password')
        developer = Developer.objects.create(user=user, company_name='test_company')
        game = Game.objects.create(developer=developer, name='test_game')
        SandboxMatch.objects.create(game=game, wager=1, key='1')

    def test_A(self):
        game = Game.objects.get(name='test_game')
        game.delete()
        self.assertEqual(SandboxMatch.objects.all().count(), 0)


class DeleteTypeTestCase(TestCase):
    """
    The sandbox match should not be deleted when the type is deleted. The type should be set to null.
    A - The match should not be deleted.
    B - The matchs type should be null.
    """
    def setUp(self):
        user = User.objects.create(email='test@email.com', user_name='test_user', password='test_password')
        developer = Developer.objects.create(user=user, company_name='test_company')
        game = Game.objects.create(developer=developer, name='test_game')
        sandbox_match_type = SandboxMatchType.objects.create(game=game, name="test_match_type")
        SandboxMatch.objects.create(game=game, type=sandbox_match_type, wager=1)
        sandbox_match_type.delete()

    def test_A(self):
        self.assertEqual(SandboxMatch.objects.count(), 1)

    def test_B(self):
        sandbox_match = SandboxMatch.objects.first()
        self.assertIsNone(sandbox_match.type)

