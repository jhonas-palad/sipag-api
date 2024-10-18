from django.core.management.base import BaseCommand, CommandError
from django.core import exceptions
from django.db.models import EmailField
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber


class Command(BaseCommand):
    help = "Used to create a admin user."
    requires_migrations_checks = True
    stealth_options = ("stdin",)

    FIELDS = ["email", "first_name", "last_name", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_model = get_user_model()

        for field in self.FIELDS:
            setattr(self, field + "_field", self.user_model._meta.get_field(field))

    def handle(self, *args, **options):
        data = {}
        for field in self.FIELDS:
            field_obj = getattr(self, field + "_field")
            while True:
                value = self.get_input_data(field_obj, field)
                if value:
                    data[field] = value
                    break

        user = self.user_model.objects.create_superuser(**data)
        print(user)

    def get_input_data(self, field, message, default=None):
        """
        Override this method if you want to customize data inputs or
        validation exceptions.
        """
        raw_value = input(message)
        if isinstance(field, PhoneNumberField):
            raw_value = PhoneNumber(country_code="63", national_number=raw_value)

        if default and raw_value == "":
            raw_value = default
        try:
            val = field.clean(raw_value, None)

            if (
                isinstance(field, EmailField)
                and self.user_model._default_manager.filter(email=raw_value).exists()
            ):
                raise exceptions.ValidationError("Email already exists")
        except exceptions.ValidationError as e:
            self.stderr.write("Error: %s" % "; ".join(e.messages))
            val = None

        return val
