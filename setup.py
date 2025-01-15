import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easyLite",  # This will be the PyPI package name
    version="1.4.1",
    author="Your Name",
    author_email="your_email@example.com",
    description="A fluent and user-friendly SQLite library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/easyLite",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
