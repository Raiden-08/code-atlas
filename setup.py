from setuptools import setup, find_packages

setup(
    name="code-atlas",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "sentence-transformers",
        "chromadb",
        "numpy"
    ],
    entry_points={
        "console_scripts": [
            "atlas=src.main:main"
        ]
    },
)
