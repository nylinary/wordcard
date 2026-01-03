from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from gtts import gTTS

from .forms import WordForm
from .models import UserWord, Word
from .services import get_linguistic_model


def home(request):
    """Главная страница с формой для добавления слов."""
    form = WordForm()
    return render(request, "words/home.html", {"form": form})


def word_lookup(request):
    """API-представление для поиска определения слова и (при необходимости) генерации аудио."""

    def _get_audio_from_text(word: Word) -> ContentFile:
        tts = gTTS(text=word.word, lang="en")
        audio_stream = BytesIO()
        tts.write_to_fp(audio_stream)
        audio_stream.seek(0)
        return ContentFile(audio_stream.read(), name=f"{word.codename}.mp3")

    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    word_text = (request.POST.get("word") or "").strip()
    if not word_text:
        return JsonResponse({"error": "Word is required"}, status=400)

    linguistic_model = get_linguistic_model()

    word = Word.objects.filter(word=word_text).first()
    if word is None:
        definition = linguistic_model.get_word_definition(word_text)
        examples = linguistic_model.get_word_examples(word_text)

        word = Word.objects.create(
            word=word_text,
            name=word_text,
            codename=word_text.lower().replace(" ", "_"),
            part_of_speech=definition.get("part_of_speech", "") or "",
            definition=(definition.get("definition") or "").capitalize(),
            examples=examples,
        )

    # Ensure audio exists (works for both local/volume and S3 storage)
    if not word.audio_file:
        content = _get_audio_from_text(word)
        word.audio_file.save(content.name, content, save=True)

    is_saved = False
    if request.user.is_authenticated:
        is_saved = UserWord.objects.filter(user=request.user, word=word).exists()

    return JsonResponse(
        {
            "word": word.word,
            "definition": word.definition,
            "examples": word.examples,
            "id": str(word.uuid),
            "is_saved": is_saved,
            "audio_file_url": word.audio_file.url if word.audio_file else "",
        }
    )


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


@login_required
@require_POST
def remove_word(request):
    """Удаление слова из коллекции пользователя."""
    word_id = request.POST.get("word_id")
    word = get_object_or_404(Word, uuid=word_id)

    # Try to find and delete the user's connection to this word
    try:
        user_word = UserWord.objects.get(user=request.user, word=word)
        user_word.delete()
        return JsonResponse({"success": True, "removed": True})
    except UserWord.DoesNotExist:
        return JsonResponse({"success": False, "error": "Word not found in your collection"}, status=404)
