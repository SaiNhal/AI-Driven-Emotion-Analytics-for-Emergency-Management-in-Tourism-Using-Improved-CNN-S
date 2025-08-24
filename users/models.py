from django.db import models

import random

def generate_unique_filename():
    # Get the last record's filename (assuming it follows a numeric pattern)
    last_record = UserLiveImagePredictinModel.objects.order_by('-id').first()
    if last_record and last_record.filename.isdigit():
        last_number = int(last_record.filename)
        # Generate a new unique number (e.g., increment by a random step)
        new_number = last_number + random.choice([1, 5, 7])  # Example: 1001, 1006, 1008 pattern
    else:
        new_number = 1001  # Starting value
    return str(new_number)

# Create your models here.
class UserRegistrationModel(models.Model):
    name = models.CharField(max_length=100)
    loginid = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=100)
    mobile = models.CharField(unique=True, max_length=100)
    email = models.CharField(unique=True, max_length=100)
    locality = models.CharField(max_length=100)
    address = models.CharField(max_length=1000)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    status = models.CharField(max_length=100)

    def __str__(self):
        return self.loginid

    class Meta:
        db_table = 'UserRegistrations'
class UserImagePredictinModel(models.Model):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    loginid = models.CharField(max_length=100)
    filename = models.CharField(max_length=100)
    emotions = models.CharField(max_length=100000)
    file = models.FileField(upload_to='files/')
    cdate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.loginid

    class Meta:
        db_table = "UserImageEmotions"


class UserLiveImagePredictinModel(models.Model):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    loginid = models.CharField(max_length=100)
    filename = models.CharField(max_length=100, default=generate_unique_filename, unique=True)
    emotions = models.CharField(max_length=100000)
    file = models.FileField(upload_to='media/frames/', max_length=500)  # Updated upload_to
    cdate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.loginid

    class Meta:
        db_table = "UserLiveImageEmotions"