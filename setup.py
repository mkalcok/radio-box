from setuptools import setup, find_packages

requirements = [
    "python-vlc",
    "pyyaml",
    "protobuf",
    "flask",
]

dev_requirements = [
    'isort',
    'mypy',
    'pylint',
    'pylint-flask',
    'pytest',
    'pytest-env',
    'pytest-mock',
    'coverage',
    'tox',
]

setup(
    name='radio_box',
    version='0.1',
    description='Internet radio streaming tool.',
    author='Martin Kalcok',
    packages=find_packages(exclude=['tests*']),
    entry_points={
        'console_scripts': [
            'radio-box-service = radio_box.service:run',
            'radio-box = radio_box.client:main',
        ],
    },
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements
    }
)
