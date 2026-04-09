from django.core.management.base import BaseCommand

from monitoring.services.demo_patients_seed import seed_demo_patients


class Command(BaseCommand):
    help = (
        "8 ta taqdimot bemoriga (4 reanimatsiya, 4 palata) mock vitallar va qisqa tarix. "
        "IDlar: demo-p-01 … demo-p-08. Real vaqt o'zgarish uchun: DEMO_VITALS_ENABLED=1"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-history",
            action="store_true",
            help="VitalHistory yozuvlarini yangilamaslik",
        )

    def handle(self, *args, **options):
        n = seed_demo_patients(refresh_history=not options["no_history"])
        self.stdout.write(
            self.style.SUCCESS(
                f"Demo bemorlar: {n} ta saqlandi. "
                f"Jonli yengil o'zgarish: env DEMO_VITALS_ENABLED=1 "
                f"(ixtiyoriy DEMO_VITALS_INTERVAL_SEC=5)."
            )
        )
