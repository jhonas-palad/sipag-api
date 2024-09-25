from django.contrib.auth import get_user_model

User = get_user_model()
class AdminUserValidator:
    message = "User must set is_staff property to true"
    code = "not_admin_user"

    def __call__(self, user):
        User.objects.get(user)
        print("user from validated user", user)
        return user


admin_user_validator = AdminUserValidator()
