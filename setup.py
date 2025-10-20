"""
Setup configuration for BRAINixIDEX Trading Bot
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text().splitlines()
    requirements = [r.strip() for r in requirements if r.strip() and not r.startswith('#')]

setup(
    name="brainixidex-trading-bot",
    version="2.0.0",
    author="SALMAN ThinkTank AI Core",
    author_email="",
    description="Advanced AI-Powered Cryptocurrency Trading Bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/salmanabjam/BRAINixIDEX-Trading-Bot",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "brainixidex=run:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.pkl", "*.csv"],
    },
    keywords="trading bot cryptocurrency ai machine-learning binance",
    project_urls={
        "Bug Reports": "https://github.com/salmanabjam/BRAINixIDEX-Trading-Bot/issues",
        "Source": "https://github.com/salmanabjam/BRAINixIDEX-Trading-Bot",
    },
)
