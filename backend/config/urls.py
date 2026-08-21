from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.generic import TemplateView


def health_check(request):
    return JsonResponse({"status": "ok", "service": "umoja-exchange-api"})


# Django template engine finds index.html in FRONTEND_BUILD_DIR (see settings).
# Every URL not matched by API/admin/static routes falls through to the Vue SPA.
spa_view = TemplateView.as_view(template_name="index.html")

urlpatterns = [
    # Internal
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),

    # REST API
    path("api/v1/auth/",      include("apps.authentication.urls")),
    path("api/v1/purchases/", include("apps.purchases.urls")),
    path("api/v1/sales/",     include("apps.sales.urls")),
    path("api/v1/dashboard/", include("apps.dashboard.urls")),
    path("api/v1/reports/",   include("apps.reports.urls")),
    path("api/v1/settings/",  include("apps.settings_app.urls")),

    # SPA catch-all — must be last
    # Regex excludes api/, admin/, static/, media/ so Django still handles those.
    re_path(r"^(?!api/|admin/|static/|media/).*$", spa_view, name="spa"),
]
