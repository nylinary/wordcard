from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import WordForm
from .models import UserWord, Word
from .services import get_linguistic_model


def home(request):
    """Главная страница с формой для добавления слов."""
    form = WordForm()
    return render(request, "words/home.html", {"form": form})


@login_required
def word_lookup(request):
    """API-представление для поиска определения слова."""
    if request.method == "POST":
        word_text = request.POST.get("word", "").strip()
        if not word_text:
            return JsonResponse({"error": "Word is required"}, status=400)

        linguistic_model = get_linguistic_model()

        if Word.objects.filter(word=word_text).exists():
            word = Word.objects.get(word=word_text)
        else:
            # Получаем определение и примеры
            definition = linguistic_model.get_word_definition(word_text)
            examples = linguistic_model.get_word_examples(word_text)

            # Сохраняем слово в базу данных, если его там еще нет
            word = Word.objects.create(
                **{
                    "word": word_text,
                    "name": word_text,
                    "codename": word_text.lower().replace(" ", "_"),
                    "part_of_speech": definition.get("part_of_speech", ""),
                    "definition": definition.get("definition", ""),
                    "examples": examples,
                }
            )

        return JsonResponse(
            {"word": word.word, "definition": word.definition, "examples": word.examples, "id": str(word.uuid)}
        )

    return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required
@require_POST
def save_word(request):
    """Сохранение слова в коллекцию пользователя."""
    word_id = request.POST.get("word_id")
    word = get_object_or_404(Word, uuid=word_id)

    user_word, created = UserWord.objects.get_or_create(user=request.user, word=word, defaults={"familiarity_score": 0})

    return JsonResponse({"success": True, "created": created})


@login_required
def my_words(request):
    """Страница с коллекцией слов пользователя."""
    user_words = UserWord.objects.filter(user=request.user).select_related("word").order_by("familiarity_score")
    return render(request, "words/my_words.html", {"user_words": user_words})


@login_required
def quiz(request):
    """Страница с квизом для проверки знаний."""
    user_words = UserWord.objects.filter(user=request.user).order_by("familiarity_score")

    if not user_words.exists():
        return render(request, "words/quiz.html", {"no_words": True})

    user_word = user_words.first()
    word = user_word.word

    # Генерация квиза
    linguistic_model = get_linguistic_model()  # например, GigaChatModel
    quiz_data = linguistic_model.generate_quiz_options(word.word)

    # Можно подстраховаться: если структура некорректная — показать заглушку
    if not quiz_data or not quiz_data.get("options") or not quiz_data.get("question"):
        return render(request, "words/quiz.html", {"no_words": True, "error": "Не удалось сгенерировать вопрос."})

    context = {
        "word": word,
        "quiz": quiz_data,
        "user_word_id": user_word.id,
    }

    return render(request, "words/quiz.html", context)


@login_required
@require_POST
def submit_quiz_answer(request):
    """Обработка ответа пользователя на вопрос квиза."""
    user_word_id = request.POST.get("user_word_id")
    selected_answer = request.POST.get("selected_answer")
    correct_answer = request.POST.get("correct_answer")

    user_word = get_object_or_404(UserWord, id=user_word_id, user=request.user)

    is_correct = selected_answer == correct_answer

    if is_correct:
        # Если ответ верный, оставляем familiarity_score как есть
        pass
    else:
        # Если неверный, увеличиваем счетчик
        user_word.familiarity_score += 1

    user_word.last_reviewed = timezone.now()
    user_word.save()

    return JsonResponse({"correct": is_correct, "next_url": request.build_absolute_uri("/words/quiz/")})
