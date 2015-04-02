from __future__ import print_function
from setuptools import setup

setup(
    name='SIPCallRecordVerify',
    version="0.1",
    url='https://github.com/LukeBeer/SIPCallRecordVerify',
    license='MIT License',
    author='Luke Berezynskyj',
    install_requires=['pjsua', 'nltk'],
    author_email='eat.lemons@gmail.com',
    description='Automated SIP call generator for verifying SIP Call Recording platforms',
    packages=['sipcallrecordverify'],
    include_package_data=True,
    platforms='any',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 1 - Alpha',
        'Natural Language :: English',
        'Environment :: CLI',
        'Intended Audience :: Voice Operations',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
)