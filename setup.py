from setuptools import setup


setup(
    name='zini',
    version='0.0.1',
    description='INI-files parser with schemes and types',
    # long_description=README,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    author='Alexander Zelenyak',
    author_email='zzz.sochi@gmail.com',
    url='',
    keywords=['ini', 'settings', 'config', 'configure', 'configuration'],
    py_modules=['zini'],
    install_requires=[],
    tests_require=['pytest'],
)
