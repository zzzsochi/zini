from setuptools import setup


setup(
    name='zini',
    version='1.1.0',
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
    url='https://github.com/zzzsochi/zini',
    keywords=['ini', 'settings', 'config', 'configure', 'configuration'],
    py_modules=['zini'],
    install_requires=["python-dateutil"],
    tests_require=['pytest'],
)
