from setuptools import setup

setup(
    name="hash_framework",
    version="0.2",
    description="Framework for studying cryptographic hash functions with SAT",
    url="http://github.com/cipherboy/hash_framework",
    author="Alexander Scheel",
    author_email="alexander.m.scheel@gmail.com",
    license="GPLv3",
    packages=["hash_framework"],
    install_requires=["psycopg2", "psutil", "flask", "cmsh"],
    zip_safe=False,
)
