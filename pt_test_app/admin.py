from django.contrib import admin

from pt_test_app.models import Question, QuestionSet


class QuestionAdmin(admin.ModelAdmin):
    pass
    
class QuestionSetAdmin(admin.ModelAdmin):
    pass    

admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionSet, QuestionSetAdmin)
