from pathlib import Path

from setuptools import find_packages, setup

_README = Path(__file__).with_name('README.md').read_text(encoding='utf-8')

setup(
    name='microclaudia_api',
    version='2.0.0',
    description='Python client for the MicroClaudia HTTP API',
    long_description=_README,
    long_description_content_type='text/markdown',
    author='Pedro Arias Ruiz',
    author_email='',
    url='https://github.com/AsiganTheSunk/microclaudia_api',
    project_urls={
        'Source': 'https://github.com/AsiganTheSunk/microclaudia_api',
        'Issues': 'https://github.com/AsiganTheSunk/microclaudia_api/issues',
    },
    license='GPL-3.0-only',
    license_files=('LICENSE',),
    packages=find_packages(exclude=('tests', 'tests.*')),
    python_requires='>=3.10',
    install_requires=[
        'requests>=2.28',
        'jsonschema>=4.18',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
