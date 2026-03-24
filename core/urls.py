from django.urls import path, include

urlpatterns = [
    # path("__reload__/", include("django_browser_reload.urls")),
    path('', include('furriel.urls'))
]
