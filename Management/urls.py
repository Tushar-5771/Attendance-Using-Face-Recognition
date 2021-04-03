from . import views
from django.urls import path

urlpatterns = [
    path('',views.Index,name='index'),
    path('Ulogin',views.Userlogin,name='login'),
    path('Capture',views.CaptureImg,name='CaptureImg'),
    path('EncodeImg',views.EncodeImg,name='EncodeImg'),
    path('RecImg',views.RecImg,name='RecImg'),
    path('SMS',views.SMS,name='SMS'),
    path('ViewStu',views.ViewStu,name='ViewStu'),
    path('getData',views.getData,name='getData'),
    path('FacultyPage',views.FacultyPage,name='FacultyPage'),
    path('logout',views.Userlogout,name='logout'),
]
