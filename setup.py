from setuptools import setup, find_packages

setup(
    name="rolax1212",
    version="2.0.6",
    author="Roland",
    description="Agent de developpement local - style Claude Code, powered by Ollama + Groq",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "rich>=13.0.0",
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "rolax1212=rolax1212.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
)
