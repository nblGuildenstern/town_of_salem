from django.core.management.base import BaseCommand
from django.db.models import F
from game.models import Role


class Command(BaseCommand):
    help = "Bump night_priority by 1 starting from a given priority"

    def add_arguments(self, parser):
        parser.add_argument(
            "start_priority",
            type=int,
            help="Night priority to start bumping from"
        )

    def handle(self, *args, **options):
        start = options["start_priority"]

        updated_count = Role.objects.filter(
            night_priority__gte=start
        ).update(
            night_priority=F("night_priority") + 1
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {updated_count} roles starting from priority {start}"
            )
        )