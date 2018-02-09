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
    # konfera
    'django>=2.0',
    'djangorestframework>=3.6',
    'django-filter>=1.1.0'
    'Pillow>=4.3.0',

    # payments
    'requests>=2.11.1',
    'fiobank>=1.2.0',
    'paypalrestsdk>=1.12.0',
]

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Framework :: Django',
    'Framework :: Django :: 2.0',
    'Intended Audience :: Customer Service',
    'Intended Audience :: Education',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Other Audience',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
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
