from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):  
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    last_login = models.DateTimeField(null=True, blank=True) 
    is_active = models.BooleanField(default=True)  
    is_staff = models.BooleanField(default=False) 
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    class Meta:
        db_table = "user"

    def __str__(self):
        return self.name

class Candidates(models.Model):
    candidate_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    
    class Meta:
        db_table = "candidates"

    def __str__(self):
        return self.name

class JobDescription(models.Model):
    job_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=False, null=False)
    required_skills = models.CharField(max_length=255)
    education_level = models.CharField(max_length=255)
    experiences_years = models.IntegerField()
    description = models.TextField()
    keywords = models.TextField(blank=True)

    class Meta:
        db_table = "job_description"

    def __str__(self):
        return f"{self.title} at {self.company} - Keywords: {self.keywords}"
    
class Resume(models.Model):
    resume_id = models.AutoField(primary_key=True)
    candidate = models.ForeignKey(Candidates, on_delete=models.CASCADE)
    job = models.ForeignKey(JobDescription, on_delete=models.CASCADE)
    file_path = models.FileField(upload_to='resumes/')
    skills = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)  # Make sure this is here
    education = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "resumes"

    def __str__(self):
        return f"{self.candidate.name} - {self.file_path.name}"


class CandidateMatch(models.Model):
    match_id = models.AutoField(primary_key=True)  # Auto-incrementing ID
    resume_id = models.IntegerField()  # ForeignKey to Resume (if applicable)
    job_id = models.IntegerField()  # ForeignKey to Job (if applicable)
    match_score = models.FloatField()  # Matching score

    class Meta:
        db_table = "candidate_matches"
    
    def __str__(self):
        return f"Match {self.match_id} - Resume {self.resume_id} - Job {self.job_id}"