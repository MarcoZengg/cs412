from django.contrib import admin

# Register your models here.
from .models import Player, Location, GameSession, Round

# -----------------------------------------------------------------------------
# Model registration: each model is registered so it appears in /admin/ and
# can be created, edited, or deleted by staff.
# -----------------------------------------------------------------------------


admin.site.register(Player)

admin.site.register(Location)

admin.site.register(GameSession)

admin.site.register(Round)