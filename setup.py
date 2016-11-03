from setuptools import setup, find_packages

setup(
    name = "odn-pargen",
    version = "0.1",
    package_dir = {'':'src'},
    packages=find_packages('src',exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=[
    ],
)
