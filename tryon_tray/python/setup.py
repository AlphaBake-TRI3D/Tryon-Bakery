from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tryon-tray",
    version="0.1.2",
    author="Your Name",
    author_email="your.email@example.com",
    description="A package for virtual try-on services integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tryon-tray",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src", include=["tryon_tray*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests",
        "python-dotenv",
        "tqdm",
        "pyjwt",
        "replicate",
    ],
    include_package_data=True,
    test_suite="tests",
) 