from pathlib import Path
from setuptools import setup, find_packages

def _requires_from_file(filename):
    with open(filename) as require_file:
        return require_file.read().splitlines()
    
this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text()

setup(
    name="magmail",
    version="0.1.0",
    license="MIT License",
    author="HEKUTA",
    author_email="Heitorhirose@gmail.com",
    url="https://github.com/HEKUCHAN/Magmail",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=_requires_from_file('requirements.txt'),
    include_package_data=True,
    classifiers=[],
    keywords=[],
    license="MIT License",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
