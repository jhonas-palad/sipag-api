from auth_api.auth_backends import UserModel
from waste.serializers import CleanerPointsSerializer


def generate_cleaner_points(**user_props):
    cleaner = UserModel.objects.get(**user_props)
    return CleanerPointsSerializer.generate_points(cleaner=cleaner)

def add_cleaner_points(cleaner):
    return CleanerPointsSerializer.add_points(cleaner=cleaner)