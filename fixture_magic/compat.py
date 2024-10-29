

def get_all_related_objects(model, exclude_fields, exclude_models):
    return [
        f for f in model._meta.get_fields() if
        (((f.one_to_many or f.one_to_one) and not f.concrete)
        or (f.many_to_many and f.auto_created))
        and f.name not in exclude_fields
        and f.related_model not in exclude_models
    ]
