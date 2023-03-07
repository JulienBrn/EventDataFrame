from distutils.core import setup


setup(
    name='event_dataframe',
    packages=['event_dataframe'],
    version='0.2',
    license='MIT',
    description = 'A simple dataframe format to store events',
    description_file = "README.md",
    author="Julien Braine",
    author_email='julienbraine@yahoo.fr',
    url='https://github.com/JulienBrn/EventDataFrame',
    download_url = 'https://github.com/JulienBrn/EventDataFrame.git',
    package_dir={'': 'src'},
    keywords=['python',  'logging'],
    install_requires=['pandas', 'matplotlib'],
)