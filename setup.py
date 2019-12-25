from setuptools import setup
import setuptools

with open('README.md') as f:
    long_description = f.read()
setup(
    name='pyscrapper',
    version='0.1.1',
    author='Pavan Kumar Yekabote',
    url='https://github.com/pavanyekabote/pyscrapper',
    long_description = long_description,
    long_description_content_type="text/markdown",
    description='A project to scrape web content as per the configuration',
    packages=setuptools.find_packages(),
    python_requires='>=3',
    install_requires=['selenium==3.141.0', 'bs4 ==0.0.1'],
    include_package_data=True
)

