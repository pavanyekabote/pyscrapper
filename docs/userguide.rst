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

* urlloaders
* observers
* managers

*UrlLoaders* are different types of url request makers such as a Web Browser,
a simple GET request anything which is capable of loading an url and give the resultant html

*Observers* are those elements which is triggered when an url loading is completed and scrapping is completed.

*Managers* manage the load balancing tasks and restrict the number requests executing parallely
as per the user's configuration. They load the url in an :file:`urlloader`, once the result is received
from the :file:`observer` then parse the html content using scrapping module, and again pushes back the final scrapped result to a user registered observer.
