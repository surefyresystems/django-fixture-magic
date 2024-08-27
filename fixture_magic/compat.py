from fixture_magic.utils import should_include


def get_all_related_objects(model, exclude_fields, exclude_models):
    return [
        f for f in model._meta.get_fields() if
        (f.one_to_many or f.one_to_one) and
        f.auto_created and not f.concrete
        and f.name not in exclude_fields
        and should_include(f.related_model, exclude_models)
    ]
