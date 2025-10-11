import os
from django.template.loaders.base import Loader as BaseLoader
from django.template import Origin, TemplateDoesNotExist
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()
class EncryptedTemplateLoader(BaseLoader):
    """
    Looks for templates with .html.enc extension and decrypts them.
    """
    supports_recursion = True

    def __init__(self, engine, dirs=None):
        super().__init__(engine)
        self.dirs = dirs or engine.dirs
        key = os.environ.get("TEMPLATE_KEY")
        print("This is the key :",key)
        if not key:
            raise RuntimeError("TEMPLATE_KEY env var is required by EncryptedTemplateLoader")
        self.fernet = Fernet(key.encode())

    def get_template_sources(self, template_name):
        # try exact name + '.enc'
        for d in self.dirs:
            candidate = str(d / (template_name + ".enc"))
            yield Origin(name=candidate, template_name=template_name, loader=self)

    def get_contents(self, origin):
        path = origin.name
        if not os.path.exists(path):
            raise TemplateDoesNotExist(origin)
        with open(path, "rb") as f:
            enc = f.read()
        try:
            data = self.fernet.decrypt(enc)
        except Exception as e:
            raise TemplateDoesNotExist(origin) from e
        return data.decode("utf-8")
