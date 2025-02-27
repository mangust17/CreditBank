from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = []

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in self.allowed_roles

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        raise PermissionDenied

class ClientRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['client']

class ReferrerRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['referrer']

class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['admin']