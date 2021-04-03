from django.db import models

# Create your models here.
class User(models.Model):
    userName = models.CharField(max_length=50)
    passWord = models.CharField(max_length=50)

    def __str__(self):
        return self.userName
    
class Faculty(models.Model):
    facultyName = models.CharField(max_length=70)
    mobileNo = models.BigIntegerField(null=False)

    def __str__(self):
        return self.facultyName
    
class Attendance(models.Model):
    Date = models.DateTimeField(null=False)
    file = models.TextField(null=False)