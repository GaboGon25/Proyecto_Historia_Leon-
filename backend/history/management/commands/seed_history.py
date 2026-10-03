from django.core.management.base import BaseCommand
from django.db import transaction
from history.models import (
    Municipality,
    Source,
    Place,
    Claim,
    Route,
    RouteStop,
    Question,
    Event,
)
from pathlib import Path
import json


class Command(BaseCommand):
    help = "Carga un catálogo editorial pendiente sin sobrescribir contenido existente."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        leon, _ = Municipality.objects.get_or_create(name="León")
        paz, _ = Municipality.objects.get_or_create(name="La Paz Centro")
        sources = []
        for code, title in [("613", "Ruins of León Viejo"), ("1236", "León Cathedral")]:
            s, _ = Source.objects.get_or_create(
                url=f"https://whc.unesco.org/en/list/{code}/",
                defaults={
                    "title": title,
                    "institution": "UNESCO · Centro del Patrimonio Mundial",
                    "notes": "Referencia institucional identificada; el acceso directo devolvió una pantalla de comprobación en vez del texto. Pendiente de consultar el registro primario y contrastar el contenido citado de INTUR.",
                },
            )
            sources.append(s)
        names = [
            ("leon-viejo", "Ruinas de León Viejo", paz, "Arqueología"),
            ("catedral", "Catedral de León", leon, "Arquitectura"),
            ("ruben-dario", "Museo y Archivo Rubén Darío", leon, "Literatura"),
            (
                "sutiaba",
                "Barrio y patrimonio cultural de Sutiaba",
                leon,
                "Memoria y tradiciones",
            ),
            (
                "san-juan",
                "Iglesia de San Juan Bautista de Sutiaba",
                leon,
                "Arquitectura",
            ),
            (
                "leyendas",
                "Museo de Leyendas y Tradiciones Coronel Joaquín de Arrechavala",
                leon,
                "Memoria y tradiciones",
            ),
            ("recoleccion", "Iglesia de La Recolección", leon, "Arquitectura"),
            ("teatro", "Teatro Municipal José de la Cruz Mena", leon, "Artes"),
        ]
        places = []
        for slug, name, municipality, category in names:
            p, created = Place.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "municipality": municipality,
                    "category": category,
                    "description": "Ficha en investigación. Lugar seleccionado en la delimitación inicial del proyecto; aún no contiene afirmaciones históricas verificadas.",
                    "context": "Se investigarán antecedentes, transformaciones y acontecimientos mediante fuentes institucionales y documentos académicos.",
                    "significance": "Se analizará su aporte a la memoria e identidad cultural sin confundir hechos históricos con tradición oral.",
                },
            )
            places.append(p)
            if created and slug in ["leon-viejo", "catedral"]:
                p.sources.add(sources[0 if slug == "leon-viejo" else 1])
        for slug, title, indices in [
            ("origenes", "Orígenes de León", [0, 1]),
            ("patrimonio", "Patrimonio y arquitectura", [1, 4, 6]),
            ("dario", "Rubén Darío", [2]),
            ("memoria", "Memoria y tradiciones", [3, 5, 7]),
        ]:
            route, created = Route.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "description": "Recorrido digital de investigación. Las paradas contienen contenido pendiente de revisión; no es una ruta física ni calcula tiempos de traslado.",
                },
            )
            if created:
                for order, index in enumerate(indices, 1):
                    RouteStop.objects.create(
                        route=route,
                        place=places[index],
                        order=order,
                        prompt="Identifica el municipio y revisa el estado de las fuentes. ¿Qué falta comprobar para explicar su importancia cultural?",
                    )
        questions = [
            (
                "¿Cómo debes interpretar una ficha marcada como pendiente?",
                [
                    "Como investigación por verificar",
                    "Como un hecho histórico demostrado",
                ],
                0,
                "La etiqueta pendiente señala que faltan fuentes consultadas y revisión histórica.",
            ),
            (
                "Si los mosaicos del mapa no cargan, ¿cómo puedes consultar los lugares?",
                ["Mediante la lista de lugares", "No se pueden consultar"],
                0,
                "La lista permite abrir cada ficha aun cuando falle el proveedor externo del mapa.",
            ),
        ]
        for prompt, options, index, explanation in questions:
            Question.objects.get_or_create(
                prompt=prompt,
                defaults={
                    "place": places[0],
                    "options": options,
                    "correct_index": index,
                    "explanation": explanation,
                },
            )
        data = json.loads(
            (
                Path(__file__).resolve().parents[2] / "data" / "initial_research.json"
            ).read_text(encoding="utf-8")
        )
        references = {}
        for entry in data["sources"]:
            values = dict(entry)
            key = values.pop("key")
            url = values.pop("url")
            references[key], _ = Source.objects.get_or_create(url=url, defaults=values)
        for entry in data["places"]:
            place = Place.objects.get(slug=entry["slug"])
            # Enrich only untouched editorial placeholders; preserve subsequent edits.
            if place.description.startswith("Ficha en investigación."):
                for key in [
                    "description",
                    "context",
                    "significance",
                    "period",
                    "latitude",
                    "longitude",
                ]:
                    if key in entry:
                        setattr(place, key, entry[key])
                for key in entry["sources"]:
                    place.sources.add(references[key])
                for claim in entry["claims"]:
                    values = dict(claim)
                    values["source"] = references[values["source"]]
                    Claim.objects.get_or_create(
                        place=place, text=values.pop("text"), defaults=values
                    )
                if entry.get("coordinate_source"):
                    place.coordinate_source = references[entry["coordinate_source"]]
                place.review_status = entry.get("review_status", "pending")
                place.full_clean()
                place.save()
        for entry in data["events"]:
            values = dict(entry)
            place = Place.objects.get(slug=values.pop("place"))
            values["source"] = references[values["source"]]
            values["verified"] = True
            Event.objects.get_or_create(
                place=place, title=values.pop("title"), defaults=values
            )
        for entry in data["questions"]:
            values = dict(entry)
            values["place"] = Place.objects.get(slug=values["place"])
            values["source"] = references[values["source"]]
            Question.objects.get_or_create(prompt=values.pop("prompt"), defaults=values)
        self.stdout.write(
            self.style.SUCCESS(
                "Catálogo cargado: 8 fichas citadas, 2 revisadas inicialmente, 4 acontecimientos respaldados por INTUR."
            )
        )
