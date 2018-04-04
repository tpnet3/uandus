NOT_PROVIDED = object()


def maybe(type_):
    """Schema field type whose value can be 'None' or 'type_'."""

    def func(val):
        if val is not None:
            return type_(val)

    return func


class Model(dict):
    schema = {}

    def __init__(self, response):
        super().__init__()
        for key, value in response.items():
            func = self.schema.get(key, NOT_PROVIDED)
            if func is NOT_PROVIDED:
                raise ValueError('%s unknown field: %r' % (type(self), key))
            if func:
                value = func(value)
            self[key] = value

    def __getattr__(self, item):
        return self[item]


class User(Model):
    schema = {
        'id': int,
        'username': str,
        'first_name': str,
        'last_name': str,
        'email': str
    }

