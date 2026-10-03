from django.test import TestCase
from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Place, Source, Event, Claim, Question, Route, Municipality


class WorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_history", verbosity=0)

    def setUp(self):
        self.client = APIClient()

    def test_seed_repeatable_preserves_edits(self):
        p = Place.objects.get(slug="catedral")
        p.description = "Edición local"
        p.save()
        call_command("seed_history", verbosity=0)
        self.assertEqual(Place.objects.count(), 8)
        self.assertEqual(Route.objects.count(), 4)
        self.assertEqual(Place.objects.get(pk=p.pk).description, "Edición local")

    def test_catalog_detail_and_filters(self):
        self.assertEqual(len(self.client.get("/api/places/").json()), 8)
        self.assertEqual(
            self.client.get("/api/places/leon-viejo/").json()["municipality"],
            "La Paz Centro",
        )
        self.assertEqual(
            len(
                self.client.get(
                    "/api/places/", {"municipality": "La Paz Centro", "q": "Viejo"}
                ).json()
            ),
            1,
        )
        self.assertEqual(self.client.get("/api/places/missing/").status_code, 404)

    def test_read_only_api(self):
        self.assertEqual(self.client.post("/api/places/", {}).status_code, 405)

    def test_coordinates_require_verified_source(self):
        p = Place.objects.get(slug="catedral")
        p.latitude = 10
        p.longitude = 10
        p.coordinate_source = None
        with self.assertRaises(ValidationError):
            p.full_clean()
        s = Source.objects.create(
            title="Fuente sintética de prueba",
            institution="Pruebas",
            url="https://example.org",
            verified=True,
        )
        p.coordinate_source = s
        p.full_clean()
        p.longitude = 200
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_reviewed_content_requires_citation(self):
        p = Place.objects.get(slug="catedral")
        p.claims.all().delete()
        p.review_status = "reviewed"
        with self.assertRaises(ValidationError):
            p.full_clean()
        s = Source.objects.create(
            title="Fuente sintética",
            institution="Pruebas",
            url="https://example.org",
            verified=True,
        )
        Claim.objects.create(
            place=p, text="Afirmación de prueba, no histórica", source=s, kind="fact"
        )
        p.full_clean()

    def test_event_source_validation(self):
        p = Place.objects.get(slug="catedral")
        s = Source.objects.get(url="https://whc.unesco.org/en/list/613/")
        e = Event(
            place=p,
            source=s,
            title="Evento sintético",
            year=2026,
            description="Prueba",
            verified=True,
        )
        with self.assertRaises(ValidationError):
            e.full_clean()

    def test_quiz_real_grading_and_invalid_answers(self):
        questions = self.client.get("/api/questions/").json()
        self.assertEqual(len(questions), 4)
        self.assertNotIn("correct_index", questions[0])
        ids = [str(q["id"]) for q in questions]
        self.assertEqual(
            self.client.post(
                "/api/quiz/grade/", {"answers": dict.fromkeys(ids, 0)}, format="json"
            ).json()["score"],
            4,
        )
        self.assertEqual(
            self.client.post(
                "/api/quiz/grade/", {"answers": dict.fromkeys(ids, 1)}, format="json"
            ).json()["score"],
            0,
        )
        self.assertEqual(
            self.client.post(
                "/api/quiz/grade/", {"answers": {}}, format="json"
            ).status_code,
            400,
        )
        self.assertEqual(
            self.client.post(
                "/api/quiz/grade/", {"answers": dict.fromkeys(ids, True)}, format="json"
            ).status_code,
            400,
        )

    def test_admin_login_edit_and_logout(self):
        url = "/admin/history/place/"
        self.assertEqual(self.client.get(url).status_code, 302)
        user = get_user_model().objects.create_superuser(
            "test-admin", password="Synthetic-Test-Only-539!"
        )
        self.assertTrue(
            self.client.login(
                username=user.username, password="Synthetic-Test-Only-539!"
            )
        )
        p = Place.objects.get(slug="catedral")
        response = self.client.post(
            f"{url}{p.id}/change/",
            {
                "name": p.name,
                "slug": p.slug,
                "municipality": p.municipality_id,
                "category": p.category,
                "period": "",
                "description": "Contenido editado en prueba",
                "context": p.context,
                "significance": p.significance,
                "review_status": "pending",
                "latitude": "",
                "longitude": "",
                "coordinate_source": "",
                "claims-TOTAL_FORMS": "0",
                "claims-INITIAL_FORMS": "0",
                "claims-MIN_NUM_FORMS": "0",
                "claims-MAX_NUM_FORMS": "1000",
                "media-TOTAL_FORMS": "0",
                "media-INITIAL_FORMS": "0",
                "media-MIN_NUM_FORMS": "0",
                "media-MAX_NUM_FORMS": "1000",
                "_save": "Guardar",
            },
        )
        self.assertEqual(response.status_code, 302)
        p.refresh_from_db()
        self.assertEqual(p.description, "Contenido editado en prueba")
        self.client.logout()
        self.assertEqual(self.client.get(url).status_code, 302)

    def test_csrf_admin_protection(self):
        c = APIClient(enforce_csrf_checks=True)
        self.assertEqual(
            c.post("/admin/login/", {"username": "bad", "password": "bad"}).status_code,
            403,
        )
