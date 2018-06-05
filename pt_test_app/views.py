import json

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core import serializers
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Count
from django.forms import Form
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User 
from django.contrib.auth.decorators import user_passes_test


from pt_test_app.models import Question, QuestionSet
from pt_test_app.forms import get_test_form_class, QuestionForm, QuestionSetForm, RegForm

def login(request):
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
        auth_login(request, form.get_user())
        return redirect('/')
    # Have no place to show errors, so redirect to main page anyway...
    return redirect('/')

def main(request):
    return render(request, 'pt_test_app/main.html')

@ensure_csrf_cookie
@user_passes_test(lambda x: x.is_staff)
def questions(request):
    return render(request, 'pt_test_app/questions.html', {
        'questions': json.dumps(list(map(Question.to_dict, Question.objects.all())))
    })

@user_passes_test(lambda x: x.is_staff)
def questions_json(request, pk=None):

    if not request.is_ajax():
        raise Http404

    try:
        body = json.loads(request.body)
    except ValueError:
        return HttpResponseBadRequest()

    instance = None
    if pk:
        instance = get_object_or_404(Question, id=pk)
    form = QuestionForm(body, instance=instance)
    if request.method in ('POST', 'PUT') and form.is_valid():
        form.instance.user = request.user
        form.save()

    if form.errors:
        return HttpResponse(
            form.errors.as_json(),
            content_type='application/json',
            status=400
        )

    return HttpResponse(
        json.dumps(form.instance.to_dict()),
        content_type='application/json',
        status=200
    )

    
@ensure_csrf_cookie
@user_passes_test(lambda x: x.is_staff)
def question_set(request, pk=None):
    instance = None
    if pk:
        instance = get_object_or_404(QuestionSet, id=pk)
    form = QuestionSetForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('question-set-view', pk='')
    return render(request, 'pt_test_app/question_set.html', {
        'question_sets': QuestionSet.objects.all(),
        'form': form
    })

@user_passes_test(lambda x: x.is_authenticated)
def test_list(request):
    return render(request, 'pt_test_app/test_list.html', {
        'tests': QuestionSet.objects.all().annotate(Count('questions'))
    })
    
@user_passes_test(lambda x: x.is_authenticated)    
def test(request, pk=None):
    if not 'test_data' in request.session:
        test_data = {'set_pk': pk, 'q_number': 0, 'result': {'success': 0}}
    else:
        test_data = request.session['test_data']
    request.session['test_data'] = test_data
    
    print('Test data:', test_data)    
    q_set = QuestionSet.objects.get(pk=test_data['set_pk'])
    q = q_set.questions.all()[test_data['q_number']]
    
    form = get_test_form_class(json.loads(q.choices))()
    return render(request, 'pt_test_app/test_step.html', {
        'text': q.text,
        'form': form
    })

@user_passes_test(lambda x: x.is_authenticated)
def submit_answer(request):
    test_data = request.session['test_data']    
    q_set = QuestionSet.objects.get(pk=test_data['set_pk'])
    
    q = q_set.questions.all()[test_data['q_number']]
    choices = json.loads(q.choices)
        
    form = get_test_form_class(choices)(request.POST or None)
    correct_indexes = []
    for index, choice in enumerate(choices):
        if choice['is_answer']:
            correct_indexes.append(index)    

    if not form.is_valid():
        print('form not valid')
        return render(request, 'pt_test_app/test_step.html', {
            'text': q.text,
            'form': form
        })    
    
    user_answers = []
    for index, f in enumerate(form.fields):
        if form.cleaned_data[f]:
            user_answers.append(index)
    if correct_indexes == user_answers:
        test_data['result']['success'] += 1
        
    if q_set.questions.count() - 1 == test_data['q_number']:
        request.session['test_data'] = test_data
        return redirect('result-view')

    print('redirect to next question')
    test_data['q_number'] += 1
    request.session['test_data'] = test_data
    return redirect('test-view', pk='')

@user_passes_test(lambda x: x.is_authenticated)
def result(request):
    if not 'test_data' in request.session:
        return redirect('/')
    test_data = request.session.pop('test_data')
    correct = test_data['result']['success']
    total = Question.objects.filter(questionset=test_data['set_pk']).count()
    return render(request, 'pt_test_app/result.html', {
        'correct': correct,
        'total': total,
        'percentage': round(100 * correct / total, 2)
    })
    
def registration(request):
   form = RegForm(request.POST or None)
   if form.is_valid():
        user = User.objects.create_user(form.cleaned_data['username'], password=form.cleaned_data['password'])
        auth_login(request, user)
        return redirect('/')
   return render(request, 'pt_test_app/registration.html', {'form': form})