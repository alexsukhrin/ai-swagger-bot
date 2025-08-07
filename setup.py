#!/usr/bin/env python3
"""
Setup script for AI Swagger Bot
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements(filename):
    with open(filename, "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-swagger-bot",
    version="0.1.0",
    author="AI Swagger Bot Team",
    author_email="team@ai-swagger-bot.com",
    description="AI-powered Swagger API bot with RAG capabilities",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/alexandrsukhryn/ai-swagger-bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.11",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
    },
    entry_points={
        "console_scripts": [
            "ai-swagger-bot=src.interactive_api_agent:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="ai, swagger, api, bot, rag, langchain, openai",
    project_urls={
        "Bug Reports": "https://github.com/alexandrsukhryn/ai-swagger-bot/issues",
        "Source": "https://github.com/alexandrsukhryn/ai-swagger-bot",
        "Documentation": "https://github.com/alexandrsukhryn/ai-swagger-bot/docs",
    },
)
