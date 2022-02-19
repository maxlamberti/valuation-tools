from setuptools import find_packages, setup

setup(
    name='valuation',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'gspread',
        'plotly'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.10'
    ]
)
