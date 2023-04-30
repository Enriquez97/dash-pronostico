from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
#from apps.graph.views import Error404View,Error505View

urlpatterns = [
    path('admin/', admin.site.urls),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('',include('apps.finanzas.urls')),
    path('user/',include('apps.users.urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
