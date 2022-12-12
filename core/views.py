from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from account.verification import PhoneVerificationManager as Verification
from .forms import SmsForm
from .serializers import PhoneNumberSerilizer, PhoneAndCodeSerilizer
from pprint import pprint
from dicttoxml import dicttoxml
import xmltodict, requests


def send_sms(data):
 
    #xml = f"""<?xml version="1.0" encoding="UTF-8"?><message><login>orozking</login><pwd>RUv6hGXN</pwd><id>A88726</id><sender>SMSPRO.KG</sender><text>sdvdvs dsdvsd vd</text><phones><phone>996776780472</phone></phones><test>1</test></message>"""
    data_dict = {'message': {
        'login': 'orozking',
        'pwd': 'RUv6hGXN',
        'id': 'A62726',
        'sender': 'SMSPRO.KG',
        'text': 'oroz 111',
        'phones': {'phone': '996776780472'},
        'test': 1
    }}
    xml = dicttoxml(data_dict, root=False, ids=False, attr_type=False, cdata=False)
    headers = {'Content-Type': 'application/xml'}
    response = requests.post('https://smspro.nikita.kg/api/message', data=xml, headers=headers)
    pprint(xmltodict.parse(response.content))
    return response.content, xml

def main(request):
    form = SmsForm()
    if request.method == 'POST':
        form = SmsForm(request.POST)
        if form.is_valid():
            response, xml = send_sms(form.cleaned_data) 
            return render(request, 'index.html', {
                'form': form, 
                'response': response, 
                'xml': xml
            })    
    return render(request, 'index.html', {'form': form, 'response': '', 'xml': ''})


class SendVerifyCode(GenericAPIView):
    
    serializer_class = PhoneNumberSerilizer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.data['phone']
        verification = Verification(phone)
        is_sent = verification.send_code()
        data = {
            'is_sent': is_sent,
            'is_blocked': verification.is_blocked(),
            'unblocked_date': str(verification.unblocked_date()),
            'left_time': verification.left_time(),
        }
        return Response(data, status=202 if is_sent else 400)
        
        
class VerificateCode(GenericAPIView):
    
    serializer_class = PhoneAndCodeSerilizer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.data['phone']
        code = serializer.data['code']
        print(code)
        verification = Verification(phone)
        is_correct = verification.verificate_code(code)
        return Response({'is_correct': is_correct}, status=202 if is_correct else 400)
        

# Create your views here.
