from channels_presence.models import Room
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Room.objects.prune_rooms()
