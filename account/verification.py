from .models import PhoneNumberVerification
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from dicttoxml import dicttoxml
from random import randint
import requests, xmltodict, datetime

class PhoneVerificationManager:
    
    phone: str
    _verification: PhoneNumberVerification
    _is_created: bool
    
    def __init__(self, phone) -> None:
        self.phone = phone
        self._verification, self._is_created = PhoneNumberVerification.objects.get_or_create(phone=self.phone)
        
    def send_code(self) -> bool:
        now = timezone.now()
        if self._verification.is_blocked:
            return False
        if self._verification.used > settings.MAX_TRY:
            self._verification.blocked_time = settings.SMS_LONG_WAITING
            self._verification.blocked_date = now
            self._verification.used = 0
            self._verification.code = self._make_code()
            self._verification.status = PhoneNumberVerification.PENDING
            self._verification.save()
            return False
        xml = self._make_xml_body()
        headers = {'Content-Type': 'application/xml'}
        response = requests.post('https://smspro.nikita.kg/api/message', data=xml, headers=headers)
        dict_response = xmltodict.parse(response.content)
        if dict_response['response']['status'] == '0' or dict_response['response']['status'] == '11':
            self._verification.used += 1
            self._verification.blocked_time = settings.SMS_SHORT_WAITING
            self._verification.blocked_date = now
            self._verification.status = PhoneNumberVerification.PENDING
        else:
            self._verification.status = PhoneNumberVerification.ERROR
        self._verification.response = response.content
        self._verification.save()
        print(self.is_blocked(), self._verification.blocked_date)
        return dict_response['response']['status'] == '0' or  dict_response['response']['status'] == '11'
    
    def verificate_code(self, code: int):
        if int(self._verification.code) == int(code):
            self._verification.status = PhoneNumberVerification.CONFIRMED
            self._verification.save()
            return True
        return False
    
    def is_blocked(self) -> bool:
        return self._verification.is_blocked
    
    def unblocked_date(self) -> datetime.datetime:
        return self._verification.unblocked_date
    
    def left_time(self) -> int:
        return self._verification.left_time
    
    def _make_code(self) -> int:
        return randint(1111, 9999)
    
    def _make_xml_body(self) -> str:
        now = timezone.now()
        data_dict = {'message': {
            'login':settings.NIKITA_USERNAME,
            'pwd': settings.NIKITA_PASSWORD,
            'id': f'{now}',
            'sender': 'SMSPRO.KG',
            'text': f"{_('Ваш код для подтверждения номера телефона')}: {self._verification.code}",
            'phones': {'phone': str(self._verification.phone)},
            'test': 1 if settings.SMS_TEST else 0
        }}
        return dicttoxml(data_dict, root=False, ids=False, attr_type=False, cdata=False)
    