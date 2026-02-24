from django.db import models

class Role(models.Model):
    TEAM_CHOICES = [
        ("town", "Town"),
        ("mafia", "Mafia"),
        ("neutral", "Neutral")
    ]
    name = models.CharField(max_length=100)
    team = models.CharField(max_length=10, choices=TEAM_CHOICES)
    mafia_priority = models.SmallIntegerField(default=0)
    virtue = models.SmallIntegerField(default=0)
    is_night_role = models.BooleanField(default=False)
    no_first_night = models.BooleanField(default=False)

    night_priority = models.IntegerField(
        null=True,
        blank=True,
        help_text="Lower number acts earlier at night"
    )
    description = models.TextField(blank=True)

    is_game_role = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    

class Player(models.Model):
    name = models.CharField(max_length=20)
    is_alive = models.BooleanField(default=True)
    role = models.CharField(max_length=20, default="")
    is_online = models.BooleanField(default=False)
    protection_level = models.IntegerField(default=0)

    attacked = models.BooleanField(default=False)
    protected = models.BooleanField(default=False)
    cursed = models.BooleanField(default=False)
    cleaned = models.BooleanField(default=False)
    blackmailed = models.BooleanField(default=False)
    on_alert = models.BooleanField(default=False)
    executionerID = models.IntegerField(default=0)


class Game(models.Model):

    selected_roles = models.JSONField(default=list)
    current_phase = models.CharField(max_length=10)
    night_number = models.IntegerField(default=0)
    current_role = models.ForeignKey(Role, null=True, on_delete=models.SET_NULL)

    def advance_night_role(self):
        from django.db.models import Q
    # Filter night roles that are in the game's selected_roles
        night_roles = list(
            Role.objects.filter(
                is_night_role=True,
                ).filter(
                    Q(id__in=self.selected_roles) | Q(is_game_role=False)   
            ).order_by("night_priority")
        )
        print(night_roles)
        if not night_roles:
            print("No night roles")
            self.current_role = None
            self.save()
            return
        print(self.current_role)
        if not self.current_role:
            # Start with the first night role
            self.current_role = night_roles[0]
            print(night_roles[0])
        else:
            try:
                current_index = night_roles.index(self.current_role)
                if current_index + 1 < len(night_roles):
                    self.current_role = night_roles[current_index + 1]
                else:
                    # End of night roles
                    self.current_role = None
            except ValueError:
                # Current role not in filtered night_roles
                self.current_role = None
        print(self.current_role)
        self.save()