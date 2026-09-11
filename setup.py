from setuptools import setup

setup(
    name='microclaudia_api',
    version='2.0',
    packages=[
        'microclaudia_api',
        'microclaudia_api.core',
        'microclaudia_api.core.auth',
        'microclaudia_api.core.requirement',
        'microclaudia_api.core.static',
        'microclaudia_api.core.static.schemas',
        'microclaudia_api.core.tools',
    ],
    install_requires=[
        'requests',
        'jsonschema',
        'pandas'
    ],
    url='',
    license='',
    author='Pedro Arias Ruiz',
    author_email='',
    description='',
)
