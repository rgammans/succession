import pathlib

from . import registry

class FileFilterJob(registry.RegisteredJob):
    def __init__(self,**kwargs):
        self.source  = pathlib.Path(kwargs.pop('source',None)).resolve()
        kwargs['target']  = pathlib.Path(kwargs.pop('target',None)).resolve()
        super().__init__(**kwargs)
        self.add_dependency(self.source)
