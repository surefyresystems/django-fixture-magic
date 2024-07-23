from django.db import models

serialize_me = []
seen = {}


def reorder_json(data, models, ordering_cond=None):
    """Reorders JSON (actually a list of model dicts).

    This is useful if you need fixtures for one model to be loaded before
    another.

    :param data: the input JSON to sort
    :param models: the desired order for each model type
    :param ordering_cond: a key to sort within a model
    :return: the ordered JSON
    """
    if ordering_cond is None:
        ordering_cond = {}
    output = []
    bucket = {}
    others = []

    for model in models:
        bucket[model] = []

    for object in data:
        if object['model'] in bucket.keys():
            bucket[object['model']].append(object)
        else:
            others.append(object)
    for model in models:
        if model in ordering_cond:
            bucket[model].sort(key=ordering_cond[model])
        output.extend(bucket[model])

    output.extend(others)
    return output


def get_fields(obj, *exclude_fields):
    try:
        return [f for f in obj._meta.fields if f.name not in exclude_fields]
    except AttributeError:
        return []


def get_m2m(obj, *exclude_fields):
    try:
        return [f for f in obj._meta.many_to_many if f.name not in exclude_fields]
    except AttributeError:
        return []


def serialize_fully(exclude_fields):
    index = 0
    exclude_fields = exclude_fields or ()

    while index < len(serialize_me):
        for field in get_fields(serialize_me[index], *exclude_fields):
            if getattr(field.related_model, "_config_model") and isinstance(field, models.ForeignKey):
                add_to_serialize_list(
                    [serialize_me[index].__getattribute__(field.name)])
        for field in get_m2m(serialize_me[index], *exclude_fields):
            if getattr(field.related_model, "_config_model"):
                add_to_serialize_list(
                    serialize_me[index].__getattribute__(field.name).all())

        index += 1

    serialize_me.reverse()


def add_to_serialize_list(objs):
    for obj in objs:
        if obj is None:
            continue
        if not hasattr(obj, '_meta'):
            add_to_serialize_list(obj)
            continue

        meta = obj._meta.proxy_for_model._meta if obj._meta.proxy else obj._meta
        model_name = getattr(meta, 'model_name',
                             getattr(meta, 'module_name', None))
        key = "%s:%s:%s" % (obj._meta.app_label, model_name, obj.pk)

        if key not in seen:
            serialize_me.append(obj)
            seen[key] = 1
