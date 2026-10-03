from django.db.models import Q
from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import (
    Place,
    Source,
    Claim,
    Event,
    MediaResource,
    Route,
    RouteStop,
    Question,
)


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = "__all__"


class ClaimSerializer(serializers.ModelSerializer):
    source = SourceSerializer()

    class Meta:
        model = Claim
        fields = ["id", "text", "source", "locator", "kind"]


class EventSerializer(serializers.ModelSerializer):
    source = SourceSerializer()
    place_slug = serializers.CharField(source="place.slug")
    place_name = serializers.CharField(source="place.name")

    class Meta:
        model = Event
        fields = "__all__"


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaResource
        fields = "__all__"


class PlaceSerializer(serializers.ModelSerializer):
    municipality = serializers.CharField(source="municipality.name")
    sources = SourceSerializer(many=True)
    claims = ClaimSerializer(many=True)
    events = EventSerializer(many=True)
    coordinate_source = SourceSerializer()
    media = serializers.SerializerMethodField()

    def get_media(self, obj):
        return MediaSerializer(obj.media.filter(approved=True), many=True).data

    class Meta:
        model = Place
        fields = "__all__"


class PlaceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PlaceSerializer
    lookup_field = "slug"

    def get_queryset(self):
        qs = (
            Place.objects.select_related("municipality", "coordinate_source")
            .prefetch_related("sources", "claims__source", "events__source", "media")
            .order_by("name")
        )
        p = self.request.query_params
        if p.get("q"):
            qs = qs.filter(
                Q(name__icontains=p["q"])
                | Q(description__icontains=p["q"])
                | Q(claims__text__icontains=p["q"])
            ).distinct()
        if p.get("municipality"):
            qs = qs.filter(municipality__name=p["municipality"])
        if p.get("category"):
            qs = qs.filter(category=p["category"])
        if p.get("period"):
            qs = qs.filter(period=p["period"])
        return qs


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.select_related("place", "source").all()
    serializer_class = EventSerializer


class StopSerializer(serializers.ModelSerializer):
    place = PlaceSerializer()

    class Meta:
        model = RouteStop
        fields = ["order", "prompt", "place"]


class RouteSerializer(serializers.ModelSerializer):
    stops = StopSerializer(many=True)

    class Meta:
        model = Route
        fields = "__all__"


class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Route.objects.prefetch_related("stops__place__municipality").all()
    serializer_class = RouteSerializer
    lookup_field = "slug"


@api_view(["GET"])
def questions(request):
    return Response(
        list(
            Question.objects.filter(active=True).values(
                "id", "place__slug", "prompt", "options"
            )
        )
    )


@api_view(["POST"])
def grade(request):
    answers = request.data.get("answers")
    if not isinstance(answers, dict):
        return Response(
            {"detail": "answers debe ser un objeto con índices de respuesta."},
            status=400,
        )
    result = []
    qs = Question.objects.filter(active=True).select_related("source", "place")
    for q in qs:
        answer = answers.get(str(q.id))
        if type(answer) is not int or not 0 <= answer < len(q.options):
            return Response(
                {"detail": "Responde todas las preguntas con una opción válida."},
                status=400,
            )
        result.append(
            {
                "id": q.id,
                "correct": answer == q.correct_index,
                "correct_answer": q.options[q.correct_index],
                "explanation": q.explanation,
                "place_slug": q.place.slug,
                "source": SourceSerializer(q.source).data if q.source else None,
            }
        )
    return Response(
        {
            "score": sum(x["correct"] for x in result),
            "total": len(result),
            "results": result,
        }
    )
