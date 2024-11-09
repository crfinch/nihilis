from setuptools import setup, find_packages

setup(
    name="nihilis",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "tcod>=11.15",
        "numpy>=1.24.0",
    ],
)