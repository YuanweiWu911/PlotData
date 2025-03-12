from setuptools import setup, find_packages

setup(
    name="PlotData",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'PyQt6>=6.4.0',
        'pandas>=1.5.0',
        'numpy>=1.23.0',
        'matplotlib>=3.6.0',
        'openpyxl>=3.0.0'
    ],
    entry_points={
        'gui_scripts': [
            'plotdata=main:main',
        ],
    },
)