from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from . import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('autenticacao.urls')),
    path('',include('plataforma.urls'))
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    