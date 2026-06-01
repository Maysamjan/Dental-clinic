"""
Role-Based Access Control for DRF.

ViewSets declare a ``module`` attribute (e.g. "patients"). The permission
class derives the required permission code from the DRF action and checks it
against the authenticated user's role permission matrix.

Permission codes look like ``"patients.view"`` / ``"billing.change"``.
A role holding the wildcard ``"*"`` (System Administrator) passes everything.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS

# Map DRF actions to a CRUD verb.
ACTION_VERB = {
    "list": "view",
    "retrieve": "view",
    "create": "add",
    "update": "change",
    "partial_update": "change",
    "destroy": "delete",
}


def role_permissions(user):
    role = getattr(user, "role", None)
    if not role:
        return set()
    return set(role.permissions or [])


def user_has_perm(user, code):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    perms = role_permissions(user)
    if "*" in perms:
        return True
    module = code.split(".")[0]
    return code in perms or f"{module}.*" in perms


class HasModulePermission(BasePermission):
    """Generic RBAC check driven by ``view.module`` + the action verb."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        module = getattr(view, "module", None)
        if not module:
            # No module declared -> only require authentication.
            return True

        # Custom @action methods may declare their own verb.
        action = getattr(view, "action", None)
        verb = getattr(view, "action_verb_override", {}).get(action)
        if not verb:
            verb = ACTION_VERB.get(action, "view" if request.method in SAFE_METHODS else "change")

        return user_has_perm(user, f"{module}.{verb}")
