"""Barcha bemorlar va ularga bog'liq yozuvlarni o'chirish (demo tozalash)."""
from django.core.management.base import BaseCommand

from monitoring.models import Patient


class Command(BaseCommand):
    help = (
        "Barcha bemorni, vital tarixini, dori/lab/qaydlarni o'chiradi. "
        "Bo'lim/palata/qurilmalar (infratuzilma) qoladi."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Tasdiqlash (sizmasdan hech narsa o'chirilmaydi)",
        )

    def handle(self, *args, **options):
        if not options["yes"]:
            self.stderr.write(
                self.style.ERROR(
                    "Xavfli operatsiya. Ishga tushirish: "
                    "python manage.py clear_monitoring_patients --yes"
                )
            )
            return
        n = Patient.objects.count()
        Patient.objects.all().delete()
        self.stdout.write(self.style.WARNING(f"O'chirildi: {n} bemor (va bog'liq yozuvlar)."))
