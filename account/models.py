from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_resized import ResizedImageField
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from random import randint
from .managers import UserManager
import datetime

  
  
class User(AbstractUser):
    
    class Meta:
        verbose_name = _('пользователь')
        verbose_name_plural = _('пользователи')
        ordering = ('-date_joined',)
        
    avatar = ResizedImageField(size=[500, 500], crop=['middle', 'center'],
        upload_to='avatars/', force_format='WEBP', quality=90, verbose_name=_('аватарка'), null=True, blank=True) 
    phone = PhoneNumberField(unique=True, verbose_name=_('номер телефона'))
    email = models.EmailField(blank=True, verbose_name=_('электронная почта'), unique=True)
    is_confirmed = models.BooleanField(_('подтверждение телефона'), default=False)
    last_activity = models.DateTimeField(blank=True, 
        null=True, verbose_name=_('последнее действие'),)
  
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    @property
    def get_full_name(self):
        return f'{self.last_name} {self.first_name}'
    get_full_name.fget.short_description = _('полное имя')    

    def __str__(self):
        return f'{self.get_full_name or str(self.phone)}'
    
    

class PhoneNumberVerification(models.Model):
    
    class Meta:
        verbose_name = _('подтверждение телефона')
        verbose_name_plural = _('подтверждение телефонов')
        ordering = ('-id', '-created_at')
    
    PENDING = 'pending' 
    CONFIRMED = 'confirmed'
    ERROR = 'error'
    
    STATUS = (
        (PENDING, 'В ожидании'),
        (CONFIRMED, 'Подтверждено'),
        (ERROR, 'Ошибка'),
    ) 
     
    
    phone = PhoneNumberField(_('номер телефона'), unique=True)
    code = models.CharField(_('код для подтверждение'), max_length=4, default=lambda: randint(1111,9999))
    created_at = models.DateField(_('дата добавление'), auto_now_add=True)
    response = models.TextField(_('ответ'), null=True, blank=True)
    status = models.CharField(_('статус'), max_length=10, choices=STATUS, default=PENDING)
    used = models.PositiveIntegerField(_('использованные попытки'), default=0)
    blocked_date = models.DateTimeField(_('Дата заблокированния'), blank=True, null=True)
    blocked_time = models.PositiveIntegerField(_('заблокированное время'), default=0,
        help_text=_('Заблокированное время указывается в секундах'))
    
    @property
    def left_time(self) -> int:
        if self.blocked_date is not None:
            now = timezone.now()
            run_away_time = now - self.blocked_date
            left_time = self.blocked_time - int(run_away_time.total_seconds())
            if left_time < 0:
                self.blocked_date = None
                self.blocked_time = 0
                self.save()
                return 0
            return left_time
        return 0
    left_time.fget.short_description = _('оставшееся время')
    
    @property
    def unblocked_date(self) -> datetime.datetime:
        if self.blocked_date is not None:
            return self.blocked_date \
                + datetime.timedelta(seconds=self.blocked_time)
        return None
    unblocked_date.fget.short_description = _('дата разблокировки')
    
    @property
    def is_blocked(self):
        if self.blocked_date is not None:
            now = timezone.now()
            return now < self.unblocked_date
        return False
    is_blocked.fget.short_description = _('заблокированно')
    
    def __str__(self) -> str:
        return f'{self.phone} - {self.status}'

# Create your models here.