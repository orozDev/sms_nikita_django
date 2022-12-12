from django.contrib.auth.models import UserManager as BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db.models import BooleanField, Case, When
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def get_queryset(self):
        now = timezone.now()
        online_time = now - timezone.timedelta(minutes=5)

        return super().get_queryset().annotate(
            online=Case(
                When(last_activity__gt=online_time, then=True),
                default=False, output_field=BooleanField()
            ),
        )
    
    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError(_('Username must be set'))
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self._create_user(username, password, **extra_fields)