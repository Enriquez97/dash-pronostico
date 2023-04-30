from django.shortcuts import render
from django.urls import path, include, re_path
from django.views.generic import ListView, CreateView,UpdateView,DeleteView,View,TemplateView
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from apps.finanzas.build.dashboards.home import Home
from apps.finanzas.build.dashboards.eeff.eeff import partidasFinancieras
from apps.finanzas.build.dashboards.eeff.estado_situacion import dashEstadoSituacion,dashEstadoSituacionPronostico
from apps.finanzas.build.dashboards.eeff.estado_gp import dashEstadoGananciasPerdidas
from django.core.cache import cache
# Create your views here.
def home(request):
    #owo=request.user.id
    dash=Home()
    context={'dashboard':dash}
    return render(request, 'home.html',context)

def pronosticoPartidas(request):
    #owo=request.user.id
    dash=partidasFinancieras()
    context={'dashboard':dash}
    return render(request, 'eeff/balance_general.html',context)

def estadoSituciacion(request):
    #owo=request.user.id
    #dash=dashEstadoSituacion()
    dash=dashEstadoSituacion()
    context={'dashboard':dash}
    return render(request, 'eeff/estado_situacion.html',context)

def estadoGananciasPerdidas(request):
    #owo=request.user.id
    dash=dashEstadoGananciasPerdidas()
    context={'dashboard':dash}
    return render(request, 'eeff/estado_gp.html',context)

