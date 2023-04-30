from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('',views.home, name='home'),
    path('pronostico-partidas/',views.pronosticoPartidas, name='pronostico'),
    path('estado-de-situacion/',views.estadoSituciacion, name='estado_situacion'),
    path('estado-de-ganancias-perdidas/',views.estadoGananciasPerdidas, name='estado_ganancias_perdidas'),
]