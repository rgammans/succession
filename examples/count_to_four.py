## We should replace this with std prelude
from succession.registry import *
from succession.shell import *

class Count(ShellJob, RegisteredJob):
    def check_self(self,):
        return False



one=Count(target="Four", command = "echo 'Four'").add_dependency("Three")
two=Count(target="Three", command = "echo 'Three'").add_dependency("Two")
three = Count(target="Two", command = "echo 'Two'").add_dependency("One")
Count(target="One", command = "echo 'One'")

resolve_all()
## Stuff below here should be done by the succession 
#  library.
import asyncio
asyncio.run(one.Run())
