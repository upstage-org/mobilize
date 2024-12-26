import re
from sqlalchemy.ext.declarative import DeclarativeMeta
from datetime import datetime


def snake_to_camel(snake_str):
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def convert_keys_to_camel_case(data):
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            new_key = snake_to_camel(key)
            new_data[new_key] = convert_keys_to_camel_case(value)
        return new_data
    elif isinstance(data, list):
        return [convert_keys_to_camel_case(item) for item in data]
    else:
        return data


def camel_to_snake(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
