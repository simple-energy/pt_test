import json
from django.db import models


class Question(models.Model):
    text = models.TextField()
    choices = models.TextField()
    

    def to_dict(self):
        return {
            'id': self.pk,
            'text': self.text,
            'choices': json.loads(self.choices)
        }
        
    def __str__(self):
        return f'Id: {self.pk} ("{self.text[:30]}...")'
        
class QuestionSet(models.Model):
    questions = models.ManyToManyField(Question)
    
    def __str__(self):
        return f'Id: {self.pk} ({self.questions.count()} questions)'