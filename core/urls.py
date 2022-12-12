from django.urls import path, include
from . import views

urlpatterns = [
   path('', views.main, name='main'), 
   path('api/auth/', include('rest_framework.urls')),
   path('api/send_verify_code/', views.SendVerifyCode.as_view(), name='send_verify_code'), 
   path('api/verificate_code/', views.VerificateCode.as_view(), name='verificate_code')
]
