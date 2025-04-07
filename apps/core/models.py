import uuid

from django.db import models


class CreatedUpdatedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class LowercaseCharField(models.CharField):
    """
    Конвертурует в нижний регистр перед сохранением или получением данных.
    """

    def to_python(self, value):
        value = super().to_python(value)
        if isinstance(value, str):
            return value.lower()
        return value


class LowercaseEmailField(models.EmailField):
    """
    Конвертурует в нижний регистр перед сохранением или получением данных.
    """

    def to_python(self, value):
        value = super().to_python(value)
        if isinstance(value, str):
            return value.lower()
        return value


class GeneralModel(CreatedUpdatedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=75, unique=True)
    codename = models.CharField(max_length=75, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        abstract = True
