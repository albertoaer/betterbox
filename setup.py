from setuptools import find_packages, setup

DEPENDENCIES = [
    'dill'
]

TEST_DEPENDENCIES = [
    'pytest'
]

setup(
    name='betterbox',
    packages=find_packages(include=('betterbox*',)),
    version='0.1.0',
    description='Python distributed services',
    author='Alberto Elorza',
    author_email='albertoelorza2002@gmail.com',
    license='MIT',
    install_requires=DEPENDENCIES,
    tests_requires=TEST_DEPENDENCIES
)