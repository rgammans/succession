How to use Succession
======================

Succession is a Python-based build automation tool similar to Make, but with explicit control over dependency checking and async execution. This guide will help you get started.

Basic Concepts
--------------

Succession uses **Jobs** to define tasks that need to be run. Jobs can have dependencies on other jobs, forming a dependency chain that Succession resolves and executes asynchronously.

Key components:

- **Job**: A task to be executed
- **Dependencies**: Other jobs that must complete before this job runs
- **Target**: A unique identifier for a registered job (usually a string or Path)
- **Successfile**: A Python file defining your jobs (like a Makefile)

Creating Your First Successfile
--------------------------------

A Successfile is a Python script that defines your build tasks. Create a file named ``Successfile`` in your project directory:

.. code-block:: python

    class MyTask(ShellJob, RegisteredJob):
        def check_self(self):
            # Return False to always run, or implement logic to check if up-to-date
            return False

    # Create a job
    MyTask(target="hello", command="echo 'Hello, World!'")

    # Set it as the default target
    add_target('default', find_target("hello"))

Run it with:

.. code-block:: bash

    succession

Core Job Classes
----------------

Job (Base Class)
~~~~~~~~~~~~~~~~

The base ``Job`` class provides the core functionality. You typically won't use this directly.

Key methods to override:

- ``check_self()``: Returns ``True`` if the job is up-to-date and doesn't need to run
- ``do_run()``: An async method that performs the actual work

ShellJob
~~~~~~~~

``ShellJob`` executes shell commands and captures their output.

.. code-block:: python

    class Build(ShellJob, RegisteredJob):
        def check_self(self):
            return False  # Always rebuild

    Build(target="build", command="gcc -o myapp main.c")

The command's stdout and stderr are automatically logged. If the command exits with a non-zero code, a ``JobFailed`` exception is raised.

RegisteredJob
~~~~~~~~~~~~~

``RegisteredJob`` allows jobs to be referenced by their target name rather than by object reference.

.. code-block:: python

    # Create jobs with targets
    RegisteredJob(target="clean", ...)
    RegisteredJob(target="build", ...)

    # Reference by name
    job.add_dependency("clean")

FileFilterJob
~~~~~~~~~~~~~

``FileFilterJob`` is designed for file transformation tasks (like compilation). It automatically handles timestamp checking.

.. code-block:: python

    class Compile(ShellJob, FileFilterJob):
        pass

    Compile(
        source="main.c",
        target="main.o",
        command="gcc -c main.c -o main.o"
    )

The job only runs if the source file is newer than the target file.

Adding Dependencies
-------------------

Dependencies define the order in which jobs must run. Use the ``add_dependency()`` method:

.. code-block:: python

    # Method 1: Chain dependencies when creating jobs
    compile_obj = Compile(target="main.o", source="main.c",
                          command="gcc -c main.c -o main.o")

    link = Build(target="myapp", command="gcc -o myapp main.o")\
        .add_dependency(compile_obj)

    # Method 2: Reference by target name (for RegisteredJob)
    Build(target="myapp", command="gcc -o myapp main.o")\
        .add_dependency("main.o")

Dependencies can be specified before the dependent job is created. Succession resolves these automatically.

The Update Check Function
--------------------------

The ``check_self()`` method determines whether a job needs to run. This gives you explicit control over the "up-to-date" decision:

.. code-block:: python

    def check_self(self):
        # Always run
        return False

    def check_self(self):
        # Run if target file doesn't exist
        return self.target.exists()

    def check_self(self):
        # Custom logic
        import os
        return os.path.exists("marker.txt")

Complete Example: Build Chain
------------------------------

Here's a complete example showing multiple compilation steps:

.. code-block:: python

    from pathlib import Path

    class Compile(ShellJob, FileFilterJob):
        """Compile a C file to object file"""
        pass

    class Link(ShellJob, RegisteredJob):
        """Link object files into executable"""
        def check_self(self):
            # Rebuild if executable doesn't exist
            return Path(self.target).exists()

    # Compile source files
    Compile(source="main.c", target="main.o",
            command="gcc -c main.c -o main.o")

    Compile(source="utils.c", target="utils.o",
            command="gcc -c utils.c -o utils.o")

    # Link into executable
    app = Link(target="myapp",
               command="gcc -o myapp main.o utils.o")\
        .add_dependency("main.o")\
        .add_dependency("utils.o")

    # Clean target
    clean = ShellJob(target="clean",
                     command="rm -f *.o myapp")

    # Set default target
    add_target('default', app)

Running Succession
------------------

Basic usage:

.. code-block:: bash

    # Run the default target
    succession

    # Run a specific target
    succession build

    # Use a different file
    succession -f MyBuildFile

    # Verbose output
    succession -v
    succession -vv  # More verbose

    # Quiet mode (only critical errors)
    succession -q

    # Disable colored output
    succession --no-colour

Command-line Options
~~~~~~~~~~~~~~~~~~~~

- ``-f, --file FILE``: Specify the Successfile (default: ``Successfile``)
- ``-v, --verbose``: Increase verbosity (can be used multiple times)
- ``-q, --quiet``: Silence all but critical errors
- ``--colour / --no-colour``: Enable/disable colored output
- ``TARGET``: Specify which target to build (default: ``default``)

Advanced Features
-----------------

Async Execution
~~~~~~~~~~~~~~~

Succession automatically runs independent jobs in parallel. If job A and B both depend on job C, but not on each other, they'll run concurrently after C completes.

Custom Job Classes
~~~~~~~~~~~~~~~~~~

Create your own job types by inheriting from ``Job``:

.. code-block:: python

    class PythonTestJob(Job, RegisteredJob):
        def __init__(self, **kwargs):
            self.test_module = kwargs.pop('module')
            super().__init__(**kwargs)

        def check_self(self):
            return False  # Always run tests

        async def do_run(self):
            import subprocess
            proc = await asyncio.create_subprocess_exec(
                'python', '-m', 'pytest', self.test_module,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            self.out = stdout.decode()
            self.err = stderr.decode()
            if proc.returncode != 0:
                raise JobFailed(self)

Common Patterns
---------------

Always Run a Task
~~~~~~~~~~~~~~~~~

.. code-block:: python

    def check_self(self):
        return False

Check File Existence
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def check_self(self):
        from pathlib import Path
        return Path(self.target).exists()

Timestamp-based (FileFilterJob handles this)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class MyCompile(ShellJob, FileFilterJob):
        pass

    MyCompile(source="input.txt", target="output.txt",
              command="process input.txt > output.txt")

Multiple Outputs from One Input
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Create a job for each output
    obj1 = Build(target="part1.o", command="...")
    obj2 = Build(target="part2.o", command="...")

    # Both depend on the same source processing
    preprocess = Build(target="preprocess", command="...")

    obj1.add_dependency(preprocess)
    obj2.add_dependency(preprocess)

Tips and Best Practices
------------------------

1. **Use RegisteredJob for reusable targets**: If you need to reference a job from multiple places, make it a RegisteredJob with a meaningful target name.

2. **FileFilterJob for file transformations**: When converting files, FileFilterJob provides automatic timestamp checking.

3. **check_self() controls execution**: Return ``False`` to always run, or implement logic based on your needs.

4. **Dependencies can be forward-referenced**: You can add a dependency by target name before creating that target.

5. **Use Path objects for file targets**: This keeps the namespace distinct from string-based target names.

6. **Leverage async**: Succession runs independent jobs concurrently, making builds faster.

7. **Default target**: Always set a ``'default'`` target for convenience:

   .. code-block:: python

       add_target('default', my_main_job)

Troubleshooting
---------------

Job not running?
  Check your ``check_self()`` implementation. If it returns ``True``, the job won't run.

Dependencies not resolved?
  Call ``resolve_all()`` if you're not using the CLI (though the CLI does this automatically).

Command failed silently?
  Use ``-v`` for verbose output to see stdout/stderr from your commands.

Import errors in Successfile?
  The Successfile is executed with succession's prelude, which imports common classes. You don't need to import ``ShellJob``, ``RegisteredJob``, etc.
