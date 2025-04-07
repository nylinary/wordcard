import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import CreatedUpdatedModel, LowercaseCharField, LowercaseEmailField


class User(AbstractUser, CreatedUpdatedModel):
    username_validator = ASCIIUsernameValidator()
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = LowercaseCharField(
        _("Username"),
        max_length=36,
        unique=True,
        help_text=_("Required. From 4 to 36 symbols. Only letters, digits and @/./+/-/_"),
        validators=[username_validator, MinLengthValidator(4)],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
        db_index=True,
    )
    first_name = models.CharField(_("First name"), max_length=128, blank=False, db_index=True)
    last_name = models.CharField(_("Last name"), max_length=128, blank=True, null=True, db_index=True)
    email = LowercaseEmailField(_("Email"), max_length=36, unique=True, blank=False, db_index=True)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
