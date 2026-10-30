"""Match an exact permission selection to complete role bundles."""


def match_permission_groups(selected, candidates):
    """Keep complete nonempty bundles and return permissions not covered by them.

    candidates contains (group_id, permission_ids) pairs. Matching never adds
    permissions: a role qualifies only when every permission it grants is selected.
    """
    selected = set(selected)
    matched = set()
    covered = set()
    for group_id, permission_ids in candidates:
        required = set(permission_ids)
        if required and required <= selected:
            matched.add(group_id)
            covered.update(required)
    return matched, selected - covered


def synchronize_permission_groups(user, selected):
    """Store exactly the selected access without modifying shared role definitions."""
    from secrets import token_hex
    from django.contrib.auth.models import Group
    from django.db import transaction
    from .models import CustomPermissionGroup, User

    with transaction.atomic():
        User.objects.select_for_update().get(pk=user.pk)
        roles = Group.objects.filter(custom_permission_bundle__isnull=True).prefetch_related('permissions')
        matched, remainder = match_permission_groups(selected, [
            (role.pk, {permission.pk for permission in role.permissions.all()})
            for role in roles
        ])
        custom = CustomPermissionGroup.objects.select_related('group').filter(owner=user).first()
        if remainder:
            if custom and custom.group.user_set.exclude(pk=user.pk).exists():
                # Never change a bundle that has been shared outside this editor.
                custom.owner = None
                custom.save(update_fields=['owner'])
                custom = None
            if custom is None:
                name = f'Custom permissions - User #{user.pk}'
                if Group.objects.filter(name=name).exists():
                    name += f' ({token_hex(4)})'
                custom = CustomPermissionGroup.objects.create(
                    owner=user, group=Group.objects.create(name=name),
                )
            custom.group.permissions.set(remainder)
            matched.add(custom.group_id)
        elif custom:
            if not custom.group.user_set.exclude(pk=user.pk).exists():
                custom.group.delete()
            else:
                custom.owner = None
                custom.save(update_fields=['owner'])
        user.groups.set(matched)
        user.user_permissions.clear()
        for key in ('_perm_cache', '_user_perm_cache', '_group_perm_cache'):
            user.__dict__.pop(key, None)
        user.__dict__.pop('_prefetched_objects_cache', None)
