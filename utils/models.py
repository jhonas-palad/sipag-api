from django.db.models import Model as DjangoModel


def to_model_dict(obj: DjangoModel, **kwargs):

    if not isinstance(obj, DjangoModel):
        raise ValueError(f"expected instance of {DjangoModel} recieved {obj.__class__}")

    obj_class = type(obj)
    include = kwargs.get("include", None) or []
    exclude = kwargs.get("exclude", None) or []

    def f(field):
        field_name = field.name
        if len(include):
            return field_name in include
        if len(exclude):
            return field_name not in exclude

        return True

    props = [field.name for field in list(filter(f, obj_class._meta.fields))]
    result = {}

    for field_name in props:
        value = getattr(obj, field_name)
        result[field_name] = value

    return result
