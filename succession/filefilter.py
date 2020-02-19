import pathlib

from . import registry

class FileFilterJob(registry.RegisteredJob):
    """A FileFilter jobs ahas a file as a source and target

    use this class to create jobs such as compile tasks, which
    take a file and produce another one.

    Source and target can be specifed as relative, or absolute
    strings are apaths and the class ensures that the targets are
    correctly registerd as normalised Paths


    :param source str|path: Source file used to check uptodate-ness
    :param target str|path: Target file created by the Job

    """
    def __init__(self,**kwargs):
        self.source  = pathlib.Path(kwargs.pop('source',None)).resolve()
        kwargs['target']  = pathlib.Path(kwargs.pop('target',None)).resolve()
        super().__init__(**kwargs)
        self.add_dependency(self.source)

    def check_self(self,):
        """Compare the mtimes of the source and target"""
        return self.target.stat().st_mtime > self.source.stat().st_mtime
