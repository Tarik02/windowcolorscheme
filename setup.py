import os
from setuptools import setup


def read(fname: str):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='windowcolorscheme',
    version='0.1.0',
    author='Tarik02',
    description='Automatically create a KDE color scheme for each window',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    license='MIT',
    keywords='Linux X11',
    url='https://github.com/Tarik02/windowcolorscheme',
    packages=['windowcolorscheme'],
    install_requires=[
        'dbus-python==1.2.12',
        'Pillow==9.3.0',
        'python-xlib==0.25',
        'six==1.13.0',
    ],
    python_requires='>=3.7.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Linux',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
        'Typing :: Typed',
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'windowcolorscheme = windowcolorscheme:main',
        ],
    },
    project_urls={
        'Issues': 'https://github.com/Tarik02/windowcolorscheme/issues',
        'Pull Requests': 'https://github.com/Tarik02/windowcolorscheme/pulls',
        'Source': 'https://github.com/Tarik02/windowcolorscheme',
    },
)
