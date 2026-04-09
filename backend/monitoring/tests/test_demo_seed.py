from django.core.management import call_command
from django.test import TestCase

from monitoring.demo_constants import DEMO_PATIENT_IDS
from monitoring.models import Patient, VitalHistory


class SeedDemoPatientsTests(TestCase):
    def test_seed_creates_eight_patients(self) -> None:
        call_command("seed_demo_patients")
        self.assertEqual(
            Patient.objects.filter(pk__in=DEMO_PATIENT_IDS).count(),
            len(DEMO_PATIENT_IDS),
        )
        p = Patient.objects.get(pk="demo-p-01")
        self.assertIn("reanimatsiya", p.room.lower())
        self.assertIsNotNone(p.last_real_vitals_ms)
        self.assertEqual(p.alarm_level, Patient.ALARM_NONE)
        h = VitalHistory.objects.filter(patient_id="demo-p-01").count()
        self.assertGreaterEqual(h, 10)

    def test_idempotent_seed(self) -> None:
        call_command("seed_demo_patients")
        call_command("seed_demo_patients", "--no-history")
        self.assertEqual(
            Patient.objects.filter(pk__in=DEMO_PATIENT_IDS).count(),
            len(DEMO_PATIENT_IDS),
        )
