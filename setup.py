from distutils.core import setup

setup(
    name='VASPmanager',
    version='0.1.0',
    author='Paul Pflugradt',
    author_email='paulpflugradt@googlemail.com',
    license='LICENSE',
    description='Tool for managing VASP calculations on a PBS based cluster',
    long_description=open('README.txt').read(),
    packages=['VASPmanager'],
)
