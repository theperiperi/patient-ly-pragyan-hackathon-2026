"""
ABDM Python Client Library Setup

Modern packaging setup with pyproject.toml support.
For configuration, see pyproject.toml
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="abdm-client",
    version="1.0.0",
    description="Official Python client library for ABDM (Ayushman Bharat Digital Mission) health data exchange",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ABDM Dev Kit Team",
    author_email="dev@abdm.gov.in",
    url="https://github.com/ABDM/abdm-client-python",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    install_requires=[
        "httpx>=0.26.0",
        "pyyaml>=6.0.1",
        "openapi-spec-validator>=0.7.0",
        "pydantic>=2.7.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.23.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "ruff>=0.1.0"
        ]
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Operating System :: OS Independent",
        "Typing :: Typed"
    ],
    keywords="abdm healthcare health-data-exchange india fhir consent abha",
    project_urls={
        "Homepage": "https://github.com/ABDM/abdm-client-python",
        "Documentation": "https://github.com/ABDM/abdm-client-python/docs",
        "Source": "https://github.com/ABDM/abdm-client-python",
        "Repository": "https://github.com/ABDM/abdm-client-python",
        "Issues": "https://github.com/ABDM/abdm-client-python/issues",
    },
    include_package_data=True,
    zip_safe=False,
)
