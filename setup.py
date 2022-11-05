from setuptools import setup, find_packages

requirements = [
    "python-vlc",
    "pyyaml",
    "protobuf<4",
    "flask",
]

dev_requirements = [
    'black',
    'flake8',
    'isort',
    'mypy',
    'mypy-protobuf',
    'pylint',
    'pylint-flask',
    'pytest',
    'pytest-cov',
    'pytest-env',
    'pytest-mock',
    'coverage',
    'types-protobuf',
    'types-PyYAML',
]

setup(
    name='radio_box',
    version='1.0',
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
