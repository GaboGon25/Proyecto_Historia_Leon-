from django.contrib import admin
from .models import (
    Municipality,
    Source,
    Place,
    Claim,
    Event,
    MediaResource,
    Route,
    RouteStop,
    Question,
)


class ClaimInline(admin.TabularInline):
    model = Claim
    extra = 0


class MediaInline(admin.TabularInline):
    model = MediaResource
    extra = 0


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ["name", "municipality", "review_status"]
    list_filter = ["municipality", "review_status", "category"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ["sources"]
    inlines = [ClaimInline, MediaInline]


class StopInline(admin.TabularInline):
    model = RouteStop
    extra = 0


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    inlines = [StopInline]


admin.site.register([Municipality, Source, Claim, Event, MediaResource, Question])
admin.site.site_header = "León en el tiempo · Administración"
