from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from .models import User, Resume, JobDescription, CandidateMatch, Candidates
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm, JobForm
from django.contrib.auth.decorators import login_required
from .utils import extract_text_from_pdf, j_extract_keywords  


# Create your views here.
def index(request):
    return render(request, 'resume_rank/index.html')

def about(request):
    return render(request, 'resume_rank/about.html')

def contact(request):
    return render(request, 'resume_rank/contact.html')

def recruit(request):
    jobs = JobDescription.objects.all()  # Get all available jobs

    if request.method == "POST" and request.FILES.get('file'):
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        job_id = request.POST.get('job_id', '').strip()
        uploaded_file = request.FILES['file']

        # Validate required fields
        if not name or not email or not job_id or not uploaded_file:
            return JsonResponse({"message": "All fields are required.", "success": False}, status=400)

        # Create or get the candidate
        candidate, created = Candidates.objects.get_or_create(email=email, defaults={'name': name})

        # Get the selected job
        try:
            job = JobDescription.objects.get(job_id=job_id)
        except JobDescription.DoesNotExist:
            return JsonResponse({"message": "Job not found", "success": False}, status=404)

        # Save the resume file
        resume = Resume(candidate=candidate, job=job, file_path=uploaded_file)
        resume.save()

        # Extract text from the uploaded PDF
        try:
            extracted_data = extract_text_from_pdf(resume.file_path.path)
            print("Extracted Data: ", extracted_data)

            # Save extracted data to respective fields in the Resume table
            resume.keywords = extracted_data.get('keywords', '')
            resume.education = extracted_data.get('education', '')
            resume.skills = extracted_data.get('skills', '')
            resume.experience = extracted_data.get('experience', '')

            # Final save after processing
            resume.save()
            print(f"Resume saved: {resume.keywords}, {resume.education}, {resume.skills}, {resume.experience}")

            return JsonResponse({"message": "Application submitted successfully!", "success": True})
        
        except Exception as e:
            print(f"Error processing resume: {e}")
            return JsonResponse({"message": "Failed to process resume.", "success": False}, status=500)
        

    return render(request, 'resume_rank/recruit.html', {'jobs': jobs})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if already logged in

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect after login
            else:
                messages.error(request, "Invalid email or password")
    else:
        form = LoginForm()

    return render(request, 'resume_rank/login.html', {'form': form})

#backend
@login_required
def dashboard(request):
    total_jobs = JobDescription.objects.count()
    total_applications = Resume.objects.count()
    total_users = User.objects.count()
    recent_applications = '5'

    context = {
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "total_users": total_users,
        "applications_today":recent_applications,
    }
    return render(request, 'resume_rank/backend/dashboard.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')

def user_list(request):
    candidates = Candidates.objects.all()
    return render(request, 'resume_rank/backend/Users.html', {'candidates': candidates})

def add_job(request):
    if request.method == "POST":
        # Handle education level and course
        education_level = request.POST.get("education_level", "")
        course = request.POST.get("course", "")
        custom_education = request.POST.get("custom_education_level", "").strip()
        custom_course = request.POST.get("custom_course", "").strip()
        title=request.POST["title"]
        company=request.POST["company"]
        required_skills=request.POST["required_skills"]
        experiences_years=request.POST.get("experiences_years")
        description=request.POST["description"]

        # Use the custom inputs if "Others" is selected
        if education_level == "others":
            education_level = custom_education

        if course.lower() == "others":
            course = custom_course

        if education_level and course:
            education_level = f"{education_level} in {course}"

        # Extract keywords
        keywords = j_extract_keywords(title, required_skills, education_level, course, description)

        # Create the JobDescription object
        job = JobDescription(
            title=title,
            company=company,
            required_skills=required_skills,
            education_level=education_level,
            experiences_years=experiences_years,
            description=description,
            keywords=keywords,
        )

        job.save()  # Keywords are generated automatically in the model

        return redirect("job_list")

    return render(request, "resume_rank/backend/add_job.html")

def job_list(request):
    jobs = JobDescription.objects.all()
    return render(request, 'resume_rank/backend/jobList.html', {'job_description': jobs})

def resume_list(request):
    resumes = Resume.objects.all()
    return render(request, 'resume_rank/backend/resumeList.html', {'resumes': resumes})


def score(request):
    candidate_matches = CandidateMatch.objects.all()
    return render(request, 'resume_rank/backend/candidateScore.html', {'candidate_matches': candidate_matches})

