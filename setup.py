import os
import sys

from setuptools import setup, find_packages

from konfera import __version__ as VERSION


def read_file(name):
    return open(os.path.join(os.path.dirname(__file__), name)).read()

if sys.argv[-1] == 'publish':
    try:
        import wheel
        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel".')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

DEPS = [
    'django>=1.10.3',
    'pytz>=2016.7',
    'fiobank>=1.2.0',
    'paypalrestsdk>=1.12.0',
    'requests>=2.11.1',
]

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Framework :: Django',
    'Framework :: Django :: 1.8',
    'Framework :: Django :: 1.9',
    'Framework :: Django :: 1.10',
    'Intended Audience :: Customer Service',
    'Intended Audience :: Education',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Other Audience',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: WSGI',
]

setup(
    name='django-konfera',
    version=VERSION,
    description='Yet another event organization app (for PyCon).',
    long_description=read_file('README.rst'),
    author='SPy o.z.',
    author_email='info [at] pycon.sk',
    url='https://github.com/pyconsk/django-konfera',
    packages=find_packages(),
    install_requires=DEPS,
    platforms='any',
    license='MIT',
    zip_safe=False,
    classifiers=CLASSIFIERS,
    include_package_data=True
)
