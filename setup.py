from setuptools import setup, find_packages

setup(
    name="crypto-sdk",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests", "requests-cache", "httpx"],
)
