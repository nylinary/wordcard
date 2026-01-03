from django.conf import settings
from django.db import models

from apps.core.models import CreatedUpdatedModel, GeneralModel, LowercaseCharField


class Word(GeneralModel):
    """Модель для хранения английских слов и фраз."""

    word = LowercaseCharField(max_length=255, unique=True, db_index=True)
    part_of_speech = models.CharField(max_length=50, blank=True, null=True)
    definition = models.TextField(blank=True, null=True)
    examples = models.JSONField(default=list, blank=True, null=True)
    audio_file = models.FileField(upload_to="tts_audio/", blank=True, null=True)

    class Meta:
        verbose_name = "Word"
        verbose_name_plural = "Words"

    def __str__(self):
        return self.word


class UserWord(CreatedUpdatedModel):
    """Связь между пользователем и словом с информацией о прогрессе изучения."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_words")
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name="user_words")
    familiarity_score = models.PositiveIntegerField(default=0)
    last_reviewed = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "User Word"
        verbose_name_plural = "User Words"
        unique_together = ("user", "word")

    def __str__(self):
        return f"{self.user.username} - {self.word.word} ({self.familiarity_score})"


class LinguisticAPIProvider(GeneralModel):
    """Модель для хранения информации о провайдерах API для определений слов."""

    api_key = models.CharField(max_length=255, blank=True, null=True)
    base_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Linguistic API Provider"
        verbose_name_plural = "Linguistic API Providers"
