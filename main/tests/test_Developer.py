import django.db
from django.test import TestCase

from main.models import User, Developer


class CreateDeveloperTestCase(TestCase):
    """
    company_name A Should not be null
                 B Should not be blank
    user C Should not be null or blank
         D User should not have more than one developer
    """
    def setUp(self):
        user = User.objects.create(email='test@email.com', user_name='test_user', password='test_password')
        User.objects.create(email='test2@email.com', user_name='test_user2', password='test_password')
        User.objects.create(email='test3@email.com', user_name='test_user3', password='test_password')
        Developer.objects.create(user=user, company_name='test_company')

    def test_developer_creation(self):
        user = User.objects.get(email='test@email.com')#
        developer = Developer.objects.get(company_name='test_company')
        self.assertEqual(developer.user, user)
        self.assertEqual(developer.company_name, 'test_company')

    def test_A(self):
        user = User.objects.get(email='test2@email.com')

        self.assertRaises(TypeError, Developer.objects.create, user=user)

    def test_B(self):
        user = User.objects.get(email='test2@email.com')

        self.assertRaises(BaseException, Developer.objects.create, user=user, company_name=' ')

    def test_C(self):
        self.assertRaises(Developer.user.RelatedObjectDoesNotExist, Developer.objects.create,
                          company_name='test_company')

    def test_D(self):
        user = User.objects.get(email='test@email.com')
        self.assertRaises(django.db.utils.IntegrityError, Developer.objects.create, user=user,
                          company_name='test_company2')


class DeleteUserTestCase(TestCase):
    """
    Tests the effect on a Developer when their user has been deleted.
    A - Developer should be deleted when the user is deleted.
    """
    def setUp(self):
        user = User.objects.create(email='test@email.com', user_name='test_user', password='test_password')
        Developer.objects.create(user=user, company_name='test_company')

    def test_A(self):
        user = User.objects.get(user_name='test_user')
        user.delete()
        self.assertEqual(Developer.objects.count(), 0)
