"""Bemorlar va (ixtiyoriy) demo infratuzilmani tozalash."""
from django.core.management.base import BaseCommand

from monitoring.models import Department, Device, Patient


class Command(BaseCommand):
    help = (
        "Barcha bemorni, vital tarixini, dori/lab/qaydlarni o'chiradi. "
        "Ixtiyoriy: --with-infrastructure — bo'lim/palata/joy/qurilmalar (demo sxema). "
        "Taqdimot demo (demo-p-01…08) ham shu buyruq bilan o'chadi."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Tasdiqlash (sizmasdan hech narsa o'chirilmaydi)",
        )
        parser.add_argument(
            "--with-infrastructure",
            action="store_true",
            help="Patientdan keyin Device va Department (CASCADE: xona, joy) ham o'chiriladi",
        )

    def handle(self, *args, **options):
        if not options["yes"]:
            self.stderr.write(
                self.style.ERROR(
                    "Xavfli operatsiya. Ishga tushirish: "
                    "python manage.py clear_monitoring_patients --yes "
                    "[--with-infrastructure]"
                )
            )
            return
        n = Patient.objects.count()
        Patient.objects.all().delete()
        self.stdout.write(self.style.WARNING(f"O'chirildi: {n} bemor (va bog'liq yozuvlar)."))

        if options["with_infrastructure"]:
            nd = Device.objects.count()
            Device.objects.all().delete()
            nc = Department.objects.count()
            Department.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Infratuzilma: {nd} qurilma, {nc} bo'lim (xona/joylar CASCADE bilan) o'chirildi."
                )
            )
