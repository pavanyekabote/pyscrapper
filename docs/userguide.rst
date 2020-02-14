##########
User Guide
##########

Installing PyScrapper
----------------------

The preferred installation method is by using `pip <http://pypi.python.org/pypi/pip/>`_::

    $ pip install pyscrapper

If you don't have pip installed, you can easily install it by downloading and running
`get-pip.py <https://bootstrap.pypa.io/get-pip.py>`_.

If, for some reason, pip won't work, you can manually `download the PyScrapper distribution
<https://pypi.python.org/pypi/pyscrapper/>`_ from PyPI, extract and then install it::

    $ python setup.py install

Code examples
-------------

The source distribution contains the :file:`examples` directory where you can find many working
examples for using PyScrapper in different ways. The examples can also be
`browsed online <https://github.com/pavanyekabote/pyscrapper/tree/master/examples>`_.

Basic Concepts
---------------

PyScrapper has an assembly module which is an assembly of base modules:

* managers
* loaders
* observers