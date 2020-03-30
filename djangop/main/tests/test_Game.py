import datetime

from django.test import TestCase

from main.exceptions import *
from main.models import User, Developer, Game


class CreateGameTestCase(TestCase):
    """
    name A Should not be null
         B Should not be blank
         C The same developer should not have two games with the same name
         D Two games can have the same name if they dont belong to the same developer
    key E Should not be blank or null
    date_created F Should not be blank or null
                 G Should not be able to set a custom value when creating a game
    developer H Should not be blank or null
    approved I Default should be false.

    """
    def setUp(self):
        user = User.objects.create(email='test@email.com', user_name='test_user', password='test_password')
        developer = Developer.objects.create(user=user, company_name='test_company')
        Game.objects.create(developer=developer, name='test_game')

        user_2 = User.objects.create(email='test2@email.com', user_name='test_user_2', password='test_password')
        Developer.objects.create(user=user_2, company_name='test_company_2')

    def test_game_creation(self):
        developer = Developer.objects.get(company_name='test_company')
        game = Game.objects.get(name='test_game')
        self.assertEqual(game.developer, developer)
        self.assertEqual(game.name, 'test_game')
        self.assertIsNotNone(game.key)
        self.assertIsNotNone(game.date_created)

    def test_A(self):
        developer = Developer.objects.get(company_name='test_company')
        self.assertRaises(GameCreateError, Game.objects.create, developer=developer)

    def test_B(self):
        developer = Developer.objects.get(company_name='test_company')
        self.assertRaises(GameCreateError, Game.objects.create, developer=developer, name=' ')

    def test_C(self):
        developer = Developer.objects.get(company_name='test_company')
        self.assertRaises(GameCreateError, Game.objects.create, developer=developer, name='test_game')

    def test_D(self):
        developer = Developer.objects.get(company_name='test_company_2')
        Game.objects.create(developer=developer, name='test_game')

    def test_E(self):
        game = Game.objects.get(name='test_game')
        self.assertIsNotNone(game.key)

    def test_F(self):
        game = Game.objects.get(name='test_game')
        self.assertIsNotNone(game.date_created)

    def test_G(self):
        developer = Developer.objects.get(company_name='test_company')
        self.assertRaises(GameCreateError, Game.objects.create, developer=developer, name='test_game_3',
                          date_created=datetime.date)

    def test_H(self):
        self.assertRaises(Game.developer.RelatedObjectDoesNotExist, Game.objects.create, name='test_game_4')

    def test_I(self):
        game = Game.objects.get(name='test_game')
        self.assertEqual(game.approved, False)


class DeleteDeveloperTestCase(TestCase):
    """
    Tests the effect on a Game when the games developer has been deleted.
    A - Game should be deleted when the developer is deleted.
    """
    def setUp(self):
        user = User.objects.create(email='test@email.com', user_name='test_user', password='test_password')
        developer = Developer.objects.create(user=user, company_name='test_company')
        Game.objects.create(developer=developer, name='test_game')

    def test_A(self):
        developer = Developer.objects.get(company_name='test_company')
        developer.delete()
        self.assertEqual(Game.objects.count(), 0)


class DeleteUserTestCase(TestCase):
    """
    Test the effect on a Game when the user belonging to the games developer is deleted.
    A - Game should be deleted when the user is deleted.
    """
    def setUp(self):
        user = User.objects.create(email='test@email.com', user_name='test_user', password='test_password')
        developer = Developer.objects.create(user=user, company_name='test_company')
        Game.objects.create(developer=developer, name='test_game')

    def test_A(self):
        user = User.objects.get(user_name='test_user')
        user.delete()
        self.assertEqual(Game.objects.count(), 0)