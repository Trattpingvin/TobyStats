from django.db import models

# Create your models here.
"""
class Sample(models.Model):
    #I am not sure if we will use DB model or use plain-text.
    #We probably don't need db, but I'm following the tutorial so it is here for now.
    
    time = models.DateTimeField("time when the sample was made")
    active_1v1 = models.IntegerField(default=0)
    queued_1v1 = models.IntegerField(default=0)
    active_ffa = models.IntegerField(default=0)
    queued_ffa = models.IntegerField(default=0)

    def __str__(self):
        return self.time
"""