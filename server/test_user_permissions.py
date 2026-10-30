from django.contrib import admin
from django.contrib.auth.models import Permission
from django.core.exceptions import FieldDoesNotExist
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import RequestFactory, TestCase, TransactionTestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


class StandardUserPermissionTests(TestCase):
    def test_superuser_creation_uses_only_standard_permission_flags(self):
        user = User.objects.create_superuser('owner@example.com', 'Owner', 'Owner-horse-729!')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_verified)
        with self.assertRaises(FieldDoesNotExist):
            User._meta.get_field('is_admin')

    def test_non_superuser_cannot_edit_or_delete_privileged_accounts(self):
        # Loading URL configuration applies the shared admin presentation.
        import server.urls  # noqa: F401
        editor = User.objects.create_user('editor@example.com', 'Editor', is_staff=True)
        editor.user_permissions.add(*Permission.objects.filter(
            content_type__app_label='users', codename__in=['change_user', 'delete_user'],
        ))
        regular = User.objects.create_user('member@example.com', 'Member')
        staff = User.objects.create_user('staff@example.com', 'Staff', is_staff=True)
        owner = User.objects.create_superuser('owner@example.com', 'Owner', 'Owner-horse-729!')
        request = RequestFactory().get('/admin/')
        request.user = editor
        model_admin = admin.site._registry[User]
        for target in (staff, owner):
            self.assertFalse(model_admin.has_change_permission(request, target))
            self.assertFalse(model_admin.has_delete_permission(request, target))
        self.assertTrue(model_admin.has_change_permission(request, regular))
        self.assertTrue(model_admin.has_delete_permission(request, regular))
        request.user = owner
        self.assertTrue(model_admin.has_change_permission(request, staff))
        self.assertTrue(model_admin.has_delete_permission(request, staff))

    def test_staff_user_list_uses_is_staff_instead_of_is_admin(self):
        staff = User.objects.create_user('staff@example.com', 'Staff', is_staff=True)
        api = APIClient()
        api.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(staff).access_token}')
        response = api.get('/api/users/list/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data[0]['is_staff'])
        self.assertNotIn('is_admin', response.data[0])


class RemoveLegacyAdminMigrationTests(TransactionTestCase):
    def test_legacy_flags_become_staff_without_granting_superuser_permissions(self):
        old_target = [('users', '0015_custompermissiongroup')]
        new_target = [('users', '0016_remove_is_admin')]

        def restore_schema():
            MigrationExecutor(connection).migrate(new_target)

        self.addCleanup(restore_schema)
        executor = MigrationExecutor(connection)
        executor.migrate(old_target)
        OldUser = executor.loader.project_state(old_target).apps.get_model('users', 'User')
        legacy = OldUser.objects.create(email='legacy@example.com', name='Legacy', password='!', is_admin=True)
        owner = OldUser.objects.create(email='owner@example.com', name='Owner', password='!', is_superuser=True)
        member = OldUser.objects.create(email='member@example.com', name='Member', password='!')
        executor = MigrationExecutor(connection)
        executor.migrate(new_target)
        NewUser = executor.loader.project_state(new_target).apps.get_model('users', 'User')
        promoted = NewUser.objects.get(pk=legacy.pk)
        self.assertTrue(promoted.is_staff)
        self.assertFalse(promoted.is_superuser)
        self.assertTrue(NewUser.objects.get(pk=owner.pk).is_staff)
        self.assertFalse(NewUser.objects.get(pk=member.pk).is_staff)
        with self.assertRaises(FieldDoesNotExist):
            NewUser._meta.get_field('is_admin')
