from django.urls import path

from . import views

app_name = "words"

urlpatterns = [
    path("", views.home, name="home"),
    path("lookup/", views.word_lookup, name="word_lookup"),
    path("save/", views.save_word, name="save_word"),
    path("my-words/", views.my_words, name="my_words"),
    path("quiz/", views.quiz, name="quiz"),
    path("quiz/submit/", views.submit_quiz_answer, name="submit_quiz_answer"),
    path("remove/", views.remove_word, name="remove_word"),
]
