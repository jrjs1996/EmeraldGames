from main.models import playerdeath
from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles


print(playerdeath.objects.filter(killer='Big Diesel'))