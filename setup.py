import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easyLite",  # This will be the PyPI package name
    version="1.6.0",
    author="eaannist",
    author_email="eaannist@gmail.com",
    description="A fluent and user-friendly SQLite library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eaannist/easyLite",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
