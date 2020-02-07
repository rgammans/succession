"""
Job registry for succession.

Add the concept of a `RegisteredJob`, which is in the Registry.

A `RegisteredJob` has a target designator, which must be a hashable python object, such as
a string or a Path object. Such a designator can be used to specify dependencies.

By convention Jobs which create filesystem entries should use Path objects as here
designators as the keeps there namespace distinct from simple names which can be `str`s

"""

from . import job


_registry_store = {}

def reset():
    """Remove all jobs from the registry"""
    global _registry_store
    _registry_store = {}

def size():
    return len(_registry_store)


def add_target(target, job):
    """Add a target designator and associated job to the registry"""
    global _registry_store
    existingjob = _registry_store.get(target, job)
    if existingjob != job:
        raise KeyError(target)
    _registry_store[target] = job

def has_target(target):
    """Returns True if target in the registy"""
    return target in _registry_store

def find_target(t):
    """Returns the job associated with the target"""
    return _registry_store[t]

class RegisteredJob(job.Job):
    """RegisteredJob auto add themeselves the the reigstry and
    can resovled dependencies on targets rather than other jobs.

    """
    def __init__(self,*args,**kwargs):
        self.target = kwargs.pop('target',None)
        self.nodelay = kwargs.pop('no_deferred_dependencies', False)
        self.unresolved = set()
        super().__init__(*args,**kwargs)
        add_target(self.target, self)


    def add_dependency(self, dep):
        if not isinstance(dep,job.Job):
            try:
                dep = find_target(dep)
            except KeyError:
                if self.nodelay: raise
                self.unresolved.add(dep)
                return

        super().add_dependency(dep)

    def resolve_dependencies(self, ):
        for d in self.unresolved:
            dep = find_target(d)
            self.add_dependency(dep)
