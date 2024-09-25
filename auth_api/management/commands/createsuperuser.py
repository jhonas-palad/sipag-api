from django.contrib.auth.management.commands.createsuperuser import (
    Command as CreateUserCommand,
)
from django.core import exceptions
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber


class Command(CreateUserCommand):
    def get_input_data(self, field, message, default=None):
        """
        Override this method if you want to customize data inputs or
        validation exceptions.
        """
        raw_value = input(message)
        if isinstance(field, PhoneNumberField):
            try:
                raw_value = PhoneNumber(country_code="63", national_number=raw_value)
            except:
                ...
        if default and raw_value == "":
            raw_value = default
        try:
            val = field.clean(raw_value, None)
        except exceptions.ValidationError as e:
            self.stderr.write("Error: %s" % "; ".join(e.messages))
            val = None

        return val
