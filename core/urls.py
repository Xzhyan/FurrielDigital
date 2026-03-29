from django.urls import path, include

urlpatterns = [
    path('', include('furriel.urls')),
    path('', include('scan.urls'))
]
