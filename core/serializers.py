from rest_framework import serializers
from rest_framework import renderers, serializers
from phonenumber_field.serializerfields import PhoneNumberField


class PhoneNumberSerilizer(serializers.Serializer):
    phone = PhoneNumberField()
    
    
class PhoneAndCodeSerilizer(serializers.Serializer):
    phone = PhoneNumberField()
    code = serializers.IntegerField(min_value=1111 ,max_value=9999)