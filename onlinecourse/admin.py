from django.contrib import admin
# <HINT> Import any new Models here
from .models import (
    Course, 
    Lesson, 
    Instructor, 
    Learner, 
    Question, 
    Choice, 
    Submission,
) 

class ChoiceInline(admin.TabularInline):
    model = Choice

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

class LessonInline(admin.StackedInline):
    model = Lesson
    list_display = ('title', 'order', 'course', 'content')
    extra = 5

class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']

class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']

admin.site.register(Question, QuestionAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)