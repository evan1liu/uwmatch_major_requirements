from setuptools import setup, find_packages

setup(
    name="uwmatch",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "motor",
        "python-dotenv",
    ],
) 