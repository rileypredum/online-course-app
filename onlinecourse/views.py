from django.shortcuts import render
from django.http import HttpResponseRedirect
# <HINT> Import any new Models here
from .models import Course, Enrollment, Question, Choice, Submission
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


def submit(request, course_id):
    # Get the user and course objects
    user = request.user
    course = get_object_or_404(Course, id=course_id)

    # Get the associated enrollment object created when the user enrolled in the course
    enrollment = get_object_or_404(Enrollment, user=user, course=course)

    if request.method == 'POST':
        # Create a submission object referring to the enrollment
        submission = Submission.objects.create(enrollment=enrollment)

        # Collect the selected choices from the exam form
        submitted_choices = []
        for key in request.POST:
            if key.startswith('choice_'):
                choice_id = int(key.split('_')[1])
                submitted_choices.append(choice_id)

        # Add each selected choice object to the submission object
        selected_choices = Choice.objects.filter(id__in=submitted_choices)
        submission.choices.set(selected_choices)

        # Redirect to show_exam_result with the submission id
        return redirect('show_exam_result', course_id=course.id, submission_id=submission.id)

    # If it's not a POST request (GET), redirect to the course detail page or any other appropriate page
    return redirect('course_detail', course_id=course.id)

def extract_answers(request):
   submitted_anwsers = []
   for key in request.POST:
       if key.startswith('choice'):
           value = request.POST[key]
           choice_id = int(value)
           submitted_anwsers.append(choice_id)
   return submitted_anwsers


def show_exam_result(request, course_id, submission_id):
    # Get course and submission based on their IDs
    course = get_object_or_404(Course, id=course_id)
    submission = get_object_or_404(Submission, id=submission_id, enrollment__user=request.user, enrollment__course=course)

    # Get the selected choice IDs from the submission record
    selected_choice_ids = submission.choices.values_list('id', flat=True)

    # Calculate the total score and question results
    total_score = 0
    question_results = []
    for question in course.questions.all():
        is_correct = all(choice.is_correct for choice in question.choices.filter(id__in=selected_choice_ids))
        score = question.points if is_correct else 0
        total_score += score
        question_results.append({'question': question, 'is_correct': is_correct, 'score': score})

    # Determine if the learner passed the exam (you can set a passing threshold here)
    passing_score_threshold = 60  # Set the passing score percentage (e.g., 60%)
    is_passed = (total_score / course.total_points) * 100 >= passing_score_threshold

    context = {
        'course': course,
        'submission': submission,
        'total_score': total_score,
        'is_passed': is_passed,
        'question_results': question_results,
    }

    return render(request, 'exam_result_bootstrap.html', context)


