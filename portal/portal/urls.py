from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from portal import settings_db_debug, settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inquery/', include('inquery.urls')),
]

if settings_db_debug.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = TemplateView.as_view(template_name="portal/404.html")
handler403 = TemplateView.as_view(template_name="portal/403.html")

