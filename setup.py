from setuptools import setup, find_packages

setup(
    name='eggshell',
    version='0.1.0',
    description='Bring GTP to your CLI',
    author='Matthias pichler',
    author_email='matthias@pichler.co.com',
    url='https://github.com/MatthiasPichler/eggshell',
    packages=find_packages(),
    install_requires=[
        'openai>=0.27.0',
    ],
    entry_points={
        'console_scripts': [
            'eggshell=eggshell.main:main',
        ],
    },
)
