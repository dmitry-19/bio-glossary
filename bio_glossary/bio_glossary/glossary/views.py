from django.shortcuts import render, redirect
from django.db.models import Count, F
from .models import Term, UserTest, UserResponse
from .forms import TermForm, TestSettingsForm
import random


def home(request):
    total_terms = Term.objects.count()
    approved_terms = Term.objects.filter(is_approved=True).count()
    return render(request, 'glossary/home.html', {
        'total_terms': total_terms,
        'approved_terms': approved_terms
    })


def add_term(request):
    if request.method == 'POST':
        form = TermForm(request.POST)
        if form.is_valid():
            new_term = form.save(commit=False)
            new_term.is_approved = True
            new_term.save()
            return redirect('success')
        else:
            return render(request, 'glossary/add_term.html', {'form': form})
    else:
        form = TermForm()
    return render(request, 'glossary/add_term.html', {'form': form})


def term_list(request):
    terms = Term.objects.filter(is_approved=True).order_by('term')
    return render(request, 'glossary/term_list.html', {'terms': terms})


def test(request):
    # Сбрасываем настройки предыдущего теста
    if 'num_questions' in request.session:
        del request.session['num_questions']

    # Инициализация сессии
    if not request.session.session_key:
        request.session.create()

    # Проверка минимального количества терминов
    approved_terms = Term.objects.filter(is_approved=True)
    if approved_terms.count() < 2:
        return render(request, 'glossary/error.html', {
            'message': 'Для прохождения теста необходимо минимум 2 одобренных термина'
        })

    # Всегда показываем форму выбора количества вопросов
    if request.method == 'POST':
        form = TestSettingsForm(request.POST)
        if form.is_valid():
            num_questions = int(form.cleaned_data['num_questions'])
            max_available = approved_terms.count()

            # Корректируем число вопросов если нужно
            num_questions = min(num_questions, max_available)

            # Генерируем новый тест
            selected_terms = random.sample(list(approved_terms), num_questions)
            questions = []

            for term in selected_terms:
                wrong_terms = list(approved_terms.exclude(id=term.id))
                num_wrong = min(3, len(wrong_terms))

                if num_wrong > 0:
                    wrong_samples = random.sample(wrong_terms, num_wrong)
                    wrong_defs = [t.definition for t in wrong_samples]
                else:
                    wrong_defs = []

                choices = wrong_defs + [term.definition]
                random.shuffle(choices)

                questions.append({
                    'term': term,
                    'choices': choices
                })

            # Сохраняем вопросы во временное хранилище
            request.session['current_test'] = {
                'questions': [
                    {
                        'term_id': q['term'].id,
                        'choices': q['choices'],
                        'correct_answer': q['term'].definition
                    } for q in questions
                ]
            }
            return render(request, 'glossary/test.html', {'questions': questions})

    # Показ формы с актуальными данными
    max_questions = approved_terms.count()
    form = TestSettingsForm(initial={'num_questions': min(10, max_questions)})
    return render(request, 'glossary/test_settings.html', {
        'form': form,
        'max_questions': max_questions
    })


def submit_test(request):
    if request.method == 'POST' and 'current_test' in request.session:
        # Обработка ответов
        test_data = request.session['current_test']
        del request.session['current_test']  # Очищаем тест

        # Сохранение результатов
        test = UserTest.objects.create(
            session_key=request.session.session_key,
            num_questions=len(test_data['questions'])
        )

        for q in test_data['questions']:
            user_answer = request.POST.get(f"term_{q['term_id']}", "")
            UserResponse.objects.create(
                test=test,
                term_id=q['term_id'],
                is_correct=(user_answer == q['correct_answer']),
                theme=Term.objects.get(id=q['term_id']).theme
            )

        return redirect('statistics')
    return redirect('home')


def statistics(request):
    total_tests = UserTest.objects.count()

    error_stats = UserResponse.objects.filter(is_correct=False) \
        .values(theme_name=F('term__theme')) \
        .annotate(total_errors=Count('id')) \
        .order_by('-total_errors')

    themes = dict(Term.THEME_CHOICES)
    for stat in error_stats:
        stat['theme_display'] = themes.get(stat['theme_name'], 'Неизвестная тема')

    total_responses = UserResponse.objects.count()
    for stat in error_stats:
        if total_responses > 0:
            stat['error_percent'] = round((stat['total_errors'] / total_responses) * 100, 1)
        else:
            stat['error_percent'] = 0.0

    return render(request, 'glossary/statistics.html', {
        'total_tests': total_tests,
        'error_stats': error_stats,
        'themes': themes
    })