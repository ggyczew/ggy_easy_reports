import os
import json
import types
from . import defaults


class Config(object):
    def __init__(self, base_path: str, **kwargs) -> None:
        self.BASE_PATH = base_path
        self.from_env()
        self.from_kwargs(**kwargs)

    def from_kwargs(self, **kwargs):
        """Set attributes from KWARGS"""
        for key, value in kwargs.items():
            setattr(self, key.upper(), value)

    def from_env(self, prefix: str = "EASY_REPORTS"):
        """Load configuration form ENVIRONMENT"""
        prefix = f'{prefix}_'
        for key in sorted(os.environ):
            if not key.startswith(prefix):
                continue

            value = os.environ[key]
            try:
                # Convert string value to python object
                value = json.loads(value)
            except Exception:
                pass

            setattr(self, key.removeprefix(prefix), value)

    def from_pyfile(self, filename):
        """Load configuration from PYFILE"""

        module = types.ModuleType('settings')
        module.__file__ = filename
        try:
            with open(self.BASE_PATH / filename, mode="rb") as f:
                exec(compile(f.read(), filename, "exec"), module.__dict__)
        except OSError as e:
            e.strerror = f'Unable to load settings file ({e.strerror})'
            raise

        # sys.path.insert(1, path)
        # module = importlib.import_module(name.split('.')[0])
        for key in dir(module):
            if not key.startswith("__") and key.isupper():
                setattr(self, key, getattr(module, key))

    def __getattribute__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            try:
                return getattr(defaults, item)
            except AttributeError as e:
                e.strerror = f"Attribute {item} not found"
                raise

    def __repr__(self):

        defaults_attrs = [
            key
            for key in vars(defaults).keys()
            if key.isupper() and not key.startswith('_')
        ]

        attrs = [
            key
            for key in vars(self).keys()
            if key.isupper() and not key.startswith('_')
        ]

        conf = '\n'.join(
            f'   {item} = {getattr(self, item)}'
            for item in sorted(list(set(attrs + defaults_attrs)))
        )
        return f'CONFIG (base):\n{conf}'
