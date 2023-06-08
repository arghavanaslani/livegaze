import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), 'r') as f:
    install_requires = f.readlines()
    
setup(
    name='livegaze',
    version='0.1.0',
    description='A Flask App to track live gaze data',
    url='https://github.com/arghavanaslani/livegaze',
    author='Arghavan Aslani',
    author_email='aslaniarghavan@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='flask livegaze',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        # other dependencies...
    ],
    entry_points={
        'console_scripts': [
            'livegaze = livegaze.app:run'
        ]
    },
)