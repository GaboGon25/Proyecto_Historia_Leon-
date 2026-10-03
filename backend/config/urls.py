from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from history.api import PlaceViewSet, EventViewSet, RouteViewSet, questions, grade

router = DefaultRouter()
router.register("places", PlaceViewSet, basename="place")
router.register("events", EventViewSet)
router.register("routes", RouteViewSet)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/questions/", questions),
    path("api/quiz/grade/", grade),
]
