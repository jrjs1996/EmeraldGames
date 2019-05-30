from django.test import TestCase

from main.exceptions import *
from main.models import User, Developer, Game, SandboxMatchType, SandboxMatchTypeGroup


class CreateSandboxMatchTypeGroup(TestCase):
    """
    name A Should not be null
         B Should not be empty
         C A match type should not have more than one match type group with the same name
         D Match type groups can have the same name if they don't belong to the same match type
    match_type E Can not be null or empty
    """
    def setUp(self):
        user = User.objects.create(email='test@email.com', user_name='test_user', password='test_password')
        developer = Developer.objects.create(user=user, company_name='test_company')
        game = Game.objects.create(developer=developer, name='test_game')
        sandbox_match_type = SandboxMatchType.objects.create(game=game, name="test_match_type")
        SandboxMatchTypeGroup.objects.create(match_type=sandbox_match_type, name="test_match_type_group")
        SandboxMatchType.objects.create(game=game, name="test_match_type_2")

    def test_sandbox_match_type_group_creation(self):
        sandbox_match_type = SandboxMatchType.objects.get(name='test_match_type')
        sandbox_match_type_group = SandboxMatchTypeGroup.objects.get(name='test_match_type_group')
        self.assertEqual(sandbox_match_type_group.name, 'test_match_type_group')
        self.assertEqual(sandbox_match_type_group.match_type, sandbox_match_type)

    def test_A(self):
        sandbox_match_type = SandboxMatchType.objects.get(name='test_match_type')
        self.assertRaises(MatchTypeGroupCreationError, SandboxMatchTypeGroup.objects.create,
                          match_type=sandbox_match_type)

    def test_B(self):
        sandbox_match_type = SandboxMatchType.objects.get(name='test_match_type')
        self.assertRaises(MatchTypeGroupCreationError, SandboxMatchTypeGroup.objects.create,
                          match_type=sandbox_match_type, name=' ')

    def test_C(self):
        sandbox_match_type = SandboxMatchType.objects.get(name='test_match_type')
        self.assertRaises(MatchTypeGroupCreationError, SandboxMatchTypeGroup.objects.create,
                          match_type=sandbox_match_type, name='test_match_type_group')

    def test_D(self):
        sandbox_match_type = SandboxMatchType.objects.get(name="test_match_type_2")
        SandboxMatchTypeGroup.objects.create(match_type=sandbox_match_type, name="test_match_type_group_2")

    def test_E(self):
        self.assertRaises(SandboxMatchTypeGroup.match_type.RelatedObjectDoesNotExist,
                          SandboxMatchTypeGroup.objects.create,
                          name='test_match_type_2')


class DeleteSandboxMatchTypeTestCase(TestCase):
    """
    Tests the effect of a MatchTypeGroups MatchType being deleted on the MatchTypeGroup.
    A - The match type group should be deleted when the match type is deleted.
    """
    def setUp(self):
        user = User.objects.create(email='test@email.com', user_name='test_user', password='test_password')
        developer = Developer.objects.create(user=user, company_name='test_company')
        game = Game.objects.create(developer=developer, name='test_game')
        sandbox_match_type = SandboxMatchType.objects.create(game=game, name="test_match_type")
        SandboxMatchTypeGroup.objects.create(match_type=sandbox_match_type, name='test_match_type_group')

    def test_A(self):
        sandbox_match_type = SandboxMatchType.objects.get(name="test_match_type")
        sandbox_match_type.delete()
        self.assertEqual(SandboxMatchTypeGroup.objects.all().count(), 0)