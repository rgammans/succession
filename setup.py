from setuptools import setup

setup(
    # Application name:
    name="Succession",

    version="0.1.0",

    author="Roger Gammans",
    author_email="rgammans@gammascience.co.uk",
    # Packages
    packages=["succession"],
    python_requires = ">3.7",
    # Include additional files into the package
    include_package_data=True,

    # Details

    license="GPLv3",
    description="A task runner with dependencies",
    install_requires=[ ],
    test_suite='tests',
    entry_points={
         "console_scripts": [
            "succession = succession.cli:start",
        ],
    }
)
