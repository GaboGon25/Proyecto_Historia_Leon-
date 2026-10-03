from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class Municipality(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Source(models.Model):
    title = models.CharField(max_length=250)
    institution = models.CharField(max_length=200)
    url = models.URLField()
    publication_date = models.CharField(max_length=80, blank=True)
    accessed_on = models.DateField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Place(models.Model):
    STATUS = [
        ("pending", "Pendiente de verificación"),
        ("reviewed", "Revisado con fuentes"),
    ]
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    municipality = models.ForeignKey(Municipality, on_delete=models.PROTECT)
    category = models.CharField(max_length=100)
    period = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    context = models.TextField(blank=True)
    significance = models.TextField(blank=True)
    review_status = models.CharField(max_length=20, choices=STATUS, default="pending")
    latitude = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    coordinate_source = models.ForeignKey(
        Source,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="located_places",
    )
    sources = models.ManyToManyField(Source, blank=True)

    def clean(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValidationError("Introduzca ambas coordenadas o deje ambas vacías.")
        if self.latitude is not None and (
            not self.coordinate_source_id or not self.coordinate_source.verified
        ):
            raise ValidationError("Las coordenadas necesitan una fuente verificada.")
        if self.review_status == "reviewed" and (
            not self.pk or not self.claims.filter(source__verified=True).exists()
        ):
            raise ValidationError(
                "Una ficha revisada necesita al menos una afirmación con fuente verificada."
            )

    def __str__(self):
        return self.name


class Claim(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="claims")
    text = models.TextField()
    source = models.ForeignKey(Source, on_delete=models.PROTECT)
    locator = models.CharField(
        max_length=250, blank=True, help_text="Página, sección o fragmento de respaldo"
    )
    kind = models.CharField(
        max_length=20,
        choices=[
            ("fact", "Hecho histórico"),
            ("oral", "Tradición oral"),
            ("proposal", "Propuesta por verificar"),
        ],
        default="proposal",
    )

    def __str__(self):
        return self.text[:80]


class Event(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=200)
    year = models.PositiveIntegerField(validators=[MaxValueValidator(2100)])
    description = models.TextField()
    source = models.ForeignKey(Source, on_delete=models.PROTECT)
    verified = models.BooleanField(default=False)

    class Meta:
        ordering = ["year", "id"]

    def clean(self):
        if self.verified and not self.source.verified:
            raise ValidationError("El acontecimiento necesita una fuente verificada.")

    def __str__(self):
        return f"{self.year}: {self.title}"


class MediaResource(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="media")
    title = models.CharField(max_length=200)
    url = models.URLField()
    kind = models.CharField(
        max_length=20,
        choices=[("image", "Imagen"), ("audio", "Audio"), ("document", "Documento")],
    )
    creator = models.CharField(max_length=200)
    license = models.CharField(max_length=200)
    permission_url = models.URLField()
    alt_text = models.CharField(max_length=300)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Route(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class RouteStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="stops")
    place = models.ForeignKey(Place, on_delete=models.PROTECT)
    order = models.PositiveIntegerField()
    prompt = models.TextField()

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["route", "order"], name="unique_route_order"
            )
        ]


class Question(models.Model):
    place = models.ForeignKey(Place, on_delete=models.PROTECT)
    prompt = models.CharField(max_length=500)
    options = models.JSONField()
    correct_index = models.PositiveIntegerField()
    explanation = models.TextField()
    source = models.ForeignKey(Source, on_delete=models.PROTECT, null=True, blank=True)
    active = models.BooleanField(default=True)

    def clean(self):
        if (
            not isinstance(self.options, list)
            or len(self.options) < 2
            or not all(isinstance(x, str) and x.strip() for x in self.options)
        ):
            raise ValidationError("Introduzca al menos dos opciones de texto.")
        if isinstance(self.options, list) and self.correct_index >= len(self.options):
            raise ValidationError("Índice de respuesta fuera de las opciones.")

    def __str__(self):
        return self.prompt
