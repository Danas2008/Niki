import json
from datetime import date, datetime, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from journey.models import Chapter

from .models import Letter, LetterState


class LetterAvailabilityTests(TestCase):
    def test_mandatory_letter_is_available_only_on_unlock_date(self):
        letter = Letter(
            number=1,
            available_at=timezone.now(),
            unlock_date=date(2026, 8, 15),
            is_mandatory=True,
        )

        self.assertFalse(letter.is_available(date(2026, 8, 14)))
        self.assertTrue(letter.is_available(date(2026, 8, 15)))
        self.assertFalse(letter.is_available(date(2026, 8, 16)))

    def test_free_choice_letter_stays_available_after_unlock_date(self):
        letter = Letter(
            number=2,
            available_at=timezone.now(),
            unlock_date=date(2026, 8, 16),
            is_mandatory=False,
        )

        self.assertFalse(letter.is_available(date(2026, 8, 15)))
        self.assertTrue(letter.is_available(date(2026, 8, 16)))
        self.assertTrue(letter.is_available(date(2026, 8, 20)))


class JarBuilderTests(TestCase):
    def setUp(self):
        self.daniel = User.objects.create_user("daniel", password="pw", is_staff=True)
        self.niki = User.objects.create_user("niki", password="pw", is_staff=False)
        self.letter = Letter.objects.get(number=9)
        self.letter.available_at = timezone.now()
        self.letter.unlock_date = timezone.localdate()
        self.letter.is_virtual = True
        self.letter.unlock_code = "N-98013"
        self.letter.save()

    def test_builder_requires_daniel(self):
        self.client.login(username="niki", password="pw")
        response = self.client.get(reverse("jar_builder"))

        self.assertEqual(response.status_code, 302)

    def test_builder_save_hashes_virtual_password(self):
        self.client.login(username="daniel", password="pw")
        response = self.client.post(
            reverse("jar_builder_save"),
            data=json.dumps({"id": self.letter.id, "field": "virtual_password", "value": "secret"}),
            content_type="application/json",
        )
        self.letter.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.letter.virtual_password, "secret")
        self.assertTrue(self.letter.virtual_password.startswith("pbkdf2_"))


class VirtualLetterFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("niki", password="pw")
        Chapter.objects.create(
            key="departure",
            title="Departure",
            teaser="",
            order=1,
            unlock_at=timezone.make_aware(datetime(2026, 8, 15)),
            manually_unlocked=True,
        )
        self.letter = Letter.objects.get(number=9)
        self.letter.available_at = timezone.now()
        self.letter.unlock_date = timezone.localdate() - timedelta(days=1)
        self.letter.is_virtual = True
        self.letter.has_code = True
        self.letter.unlock_code = "N-98013"
        self.letter.virtual_password = ""
        self.letter.virtual_content = "Secret content"
        self.letter.save()
        self.client.login(username="niki", password="pw")

    def test_redeem_code_routes_to_virtual_unlock(self):
        response = self.client.post(reverse("jar_redeem"), {"code": "N-98013"})

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("letter_virtual_unlock", kwargs={"number": 9}), response["Location"])

    def test_correct_virtual_password_opens_letter(self):
        from django.contrib.auth.hashers import make_password

        self.letter.virtual_password = make_password("secret")
        self.letter.save(update_fields=["virtual_password"])

        response = self.client.post(
            reverse("letter_virtual_unlock", kwargs={"number": 9}),
            {"code": "N-98013", "password": "secret"},
        )

        self.assertRedirects(response, reverse("letter_detail", kwargs={"number": 9}))
        self.assertTrue(LetterState.objects.get(letter=self.letter).opened)
