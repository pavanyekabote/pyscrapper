from setuptools import setup
import setuptools

with open('README.rst') as f:
    long_description = f.read()
setup(
    name='pyscrapper',
    version='0.1.3',
    author='Pavan Kumar Yekabote',
    url='https://github.com/pavanyekabote/pyscrapper',
    long_description = long_description,
    long_description_content_type="text/x-rst",
    description='A configurable web scrapping tool',
    packages=setuptools.find_packages(),
    python_requires='>=3',
    install_requires=['selenium==3.141.0', 'bs4 ==0.0.1', 'urllib3==1.26.5'],
    include_package_data=True
)

