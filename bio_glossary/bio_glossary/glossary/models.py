from django.db import models


class Term(models.Model):
    THEME_CHOICES = [
        ('cell', 'Клеточная биология'),
        ('genetics', 'Генетика'),
        ('evolution', 'Эволюция'),
        ('ecology', 'Экология'),
    ]

    term = models.CharField(max_length=100, unique=True)
    definition = models.TextField()
    theme = models.CharField(max_length=50, choices=THEME_CHOICES)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.term

class UserTest(models.Model):
    session_key = models.CharField(max_length=40)
    num_questions = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class UserResponse(models.Model):
    test = models.ForeignKey(UserTest, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    theme = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)