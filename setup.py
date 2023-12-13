"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-environment.git
Description       : pip setup file.
License           : GPL3
"""

from setuptools import setup, find_packages

setup(
    name='vixen_lib',
    version='0.0.1',
    description='Vixen Manager',
    packages=find_packages(),
    url='https://github.com/vixen-shell/vixen-environment.git',
    license='GPL3',
    author='Nohavye',
    author_email='noha.poncelet@gmail.com',
    python_requires='>=3.11.6'
)