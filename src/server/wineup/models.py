from django.db import models


class Wine(models.Model):
    internal_id = models.CharField(null=True, blank=True, unique=True, max_length=500)
    all_names = models.CharField(null=True, max_length=2000)


class User(models.Model):
    internal_id = models.CharField(null=True, blank=True, unique=True, max_length=500)


class Review(models.Model):
    rating = models.IntegerField()
    variants = models.IntegerField()
    wine = models.ForeignKey(Wine, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("wine", "user")
