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
a simple GET request etc., anything which is capable of loading an url and give the resultant html

*Observers* are those elements, which are triggered when an url loading is completed and scrapping is completed.

*Managers* manage the load balancing tasks and restrict the number requests executing parallely
as per the user's configuration. They load the url in an :file:`urlloader`, once the result is received
from the :file:`observer` then parse the html content using scrapping module, and again pushes back the final scrapped result to a user registered observer.


Now you might have got an abstract idea, on what each module of assembly does. Let's have deep dive into each of these modules.

Observers
---------
:mod:`pyscrapper.assembly.observers`

The observers module has two interfaces

* **Observable** :
        * An Observable can hold a list of observers.
        * When an event occurs, such as url loaded / scraping completed , then all the observers are notified with the change.
* **Observer** :
    * An Observer is capable of listening to a change and trigger the corresponding operations.

UrlLoaders
----------
:mod:`pyscrapper.assembly.urlloaders`

* The UrlLoader interface inherits the Observable interface
* Any class implementing the UrlLoader interface is capable of holding and notifying a list of observers.

Managers
----------
:mod:`pyscrapper.assembly.managers`

* Manager acts both, as Observable to the user requests and Observer to the UrlLoader
* As an Observable, the manager holds all the Observers, defined by the user / developer, who are interested in receiving data when published.
* As an Observer, the manager becomes is registered with UrlLoader( which is also an Observable ), to get notified on url response is received.

Scrape Config
--------------

* To scrape web content, you must define

    * The url of the webpage
    * The configuration, which allows the scrapper understand which parts of the html do you want to scrape.

.. note:: Refer :ref:`scrape-reflabel` page for detailed explanation on configurations.

